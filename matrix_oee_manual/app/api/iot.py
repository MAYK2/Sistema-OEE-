from flask import Blueprint, request, jsonify
from datetime import datetime
from app.extensions import db
from app.models.work_order import WorkOrder, WorkOrderStatus
from app.models.downtime import DowntimeEvent
from app.models.line import Line

iot_bp = Blueprint('iot', __name__)

@iot_bp.route('/telemetria', methods=['POST'])
def receive_telemetry():
    """
    Recibe los datos en tiempo real desde el ESP32.
    Formato esperado (JSON):
    {
      "line_id": 1, 
      "produced_count": 5, 
      "machine_status": "running" // o "stopped"
    }
    """
    data = request.get_json()
    
    # --- LOGGING SYSTEM FOR FRONTEND ---
    global telemetry_logs
    if 'telemetry_logs' not in globals():
        telemetry_logs = []
    
    log_entry = {
        "time": datetime.now().strftime("%H:%M:%S"),
        "payload": data,
        "ip": request.remote_addr
    }
    telemetry_logs.insert(0, log_entry)
    telemetry_logs = telemetry_logs[:50] # Keep last 50
    # -----------------------------------
    
    print("🤖 RECIBIDO DESDE ESP32:", data)
    
    if not data:
        return jsonify({"error": "No JSON payload provided"}), 400

    line_id = data.get('line_id')
    produced_count = data.get('produced_count', 0)
    machine_status = data.get('machine_status')
    
    # Optional Timestamp from ESP32 (ISO 8601 format: YYYY-MM-DDTHH:MM:SS)
    timestamp_str = data.get('timestamp')
    event_time = datetime.now()
    if timestamp_str:
        try:
            event_time = datetime.fromisoformat(timestamp_str)
        except ValueError:
            pass # Fallback to server time if format is invalid

    if not line_id or not machine_status:
        return jsonify({"error": "Missing required fields (line_id, machine_status)"}), 400

    # Ensure transaction isolation
    db.session.remove()

    # Buscar la Línea para validación (opcional si la DB lo restringe)
    line = Line.query.get(line_id)
    if not line:
         return jsonify({"error": "Invalid line_id"}), 404

    # Buscar OT activa para esta línea.
    # Necesitamos hacer un JOIN con Product para saber a qué línea pertenece la OT.
    from app.models.product import Product
    active_order = WorkOrder.query.join(Product).filter(
        Product.line_id == line_id,
        WorkOrder.status.in_([WorkOrderStatus.EXECUTION, WorkOrderStatus.PENDING])
    ).first()

    if not active_order:
        # Si la máquina está andando pero no hay OT activa, podríamos registrar un "Tiempo No Planeado",
        # pero por ahora simplemente ignoramos el conteo para no afectar datos.
        return jsonify({"message": "Telemetry received, but no active WorkOrder found for this line."}), 200

    # 1. LÓGICA DE ESTADOS AUTOMÁTICOS
    current_status = active_order.status
    response_msg = f"Telemetry processed for OT {active_order.ot_number}."

    if machine_status == "stopped" and current_status == WorkOrderStatus.EXECUTION:
        # La máquina se paró de golpe. Pasamos a PENDING (Pausa) y creamos Downtime.
        active_order.status = WorkOrderStatus.PENDING
        
        downtime = DowntimeEvent(
            work_order_id=active_order.id,
            reason="Automático: Pendiente de justificar", # Trigger word for the frontend
            comment="Detención detectada automáticamente por el sensor",
            start_time=event_time
        )
        db.session.add(downtime)
        response_msg += " Machine stopped, auto-paused WorkOrder."
        
    elif machine_status == "stopped" and current_status == WorkOrderStatus.PENDING:
        # Ignorar señales de paro repetidas si la máquina YA está detenida
        response_msg += " Machine already stopped, no action taken."

    elif machine_status == "running" and current_status == WorkOrderStatus.PENDING:
        # La máquina volvió a arrancar. Verificamos si estaba detenida por una parada automática.
        # Buscamos el último evento abierto.
        open_downtime = DowntimeEvent.query.filter_by(
            work_order_id=active_order.id, 
            end_time=None
        ).order_by(DowntimeEvent.start_time.desc()).first()

        if open_downtime: # Sea cual sea el motivo de la parada, si la máquina arrancó de verdad, la cerramos.
            open_downtime.end_time = event_time
            delta = open_downtime.end_time - open_downtime.start_time
            open_downtime.duration_seconds = int(delta.total_seconds())
            
        # Volvemos la OT a Ejecución
        active_order.status = WorkOrderStatus.EXECUTION
        response_msg += " Machine started, auto-resumed WorkOrder."

    # 2. ACTUALIZAR CONTEO
    # Se hace DESPUÉS de los cambios de estado para que si vuelve a arrancar en este mismo JSON, cuente los bidones de este paquete.
    if produced_count > 0 and active_order.status == WorkOrderStatus.EXECUTION:
        active_order.total_produced += produced_count

    db.session.commit()
    
    return jsonify({
        "message": response_msg,
        "ot_number": active_order.ot_number,
        "current_total_produced": active_order.total_produced,
        "machine_status_applied": machine_status,
        "ot_status": active_order.status.name
    }), 200

@iot_bp.route('/logs', methods=['GET'])
def view_logs():
    """
    Ruta de depuración para ver qué datos están entrando en tiempo real.
    """
    global telemetry_logs
    if 'telemetry_logs' not in globals():
        return jsonify([])
    return jsonify(telemetry_logs)
