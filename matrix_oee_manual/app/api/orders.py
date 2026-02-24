from flask import Blueprint, request, jsonify
from flask_login import login_required
from app.extensions import db
from app.models.work_order import WorkOrder, WorkOrderStatus
from app.models.downtime import DowntimeEvent
from datetime import datetime

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/', methods=['POST'])
def create_order():
    data = request.get_json()
    if not data or 'ot_number' not in data or 'product_id' not in data:
        return jsonify({"error": "Missing required fields"}), 400
        
    new_order = WorkOrder(
        ot_number=data['ot_number'],
        client_name=data.get('client_name', 'Unknown'),
        product_id=data['product_id'],
        status=WorkOrderStatus.PENDING
    )
    
    db.session.add(new_order)
    db.session.commit()
    
    return jsonify({
        "id": new_order.id,
        "ot_number": new_order.ot_number,
        "status": new_order.status.value
    }), 201

@orders_bp.route('/<int:id>/start', methods=['POST'])
@login_required
def start_order(id):
    db.session.remove() 

    order = WorkOrder.query.get_or_404(id)
    data = request.get_json() or {}
    
    open_downtime = DowntimeEvent.query.filter_by(work_order_id=order.id, end_time=None)\
                                       .order_by(DowntimeEvent.start_time.desc())\
                                       .first()
    
    if open_downtime:
        open_downtime.end_time = datetime.now()
        delta = open_downtime.end_time - open_downtime.start_time
        open_downtime.duration_seconds = int(delta.total_seconds())
        db.session.add(open_downtime)
        db.session.commit()

    if order.status == WorkOrderStatus.PENDING:
        order.status = WorkOrderStatus.EXECUTION
        
        if not order.start_time: 
            order.start_time = datetime.now()
            
        if 'operators_count' in data:
            order.operators_count = int(data['operators_count'])
            
        db.session.commit()
        
        with open('/tmp/matrix_debug.log', 'a') as f:
             f.write(f"DEBUG_START: OT={order.ot_number} ID={order.id}\n")
             f.write(f"   Set StartTime={order.start_time}\n")
        
        return jsonify({
            "message": "Order started", 
            "status": order.status.value, 
            "start_time": order.start_time.isoformat()
        })
    
    return jsonify({"error": "Invalid status transition"}), 400

@orders_bp.route('/<int:id>/pause', methods=['POST'])
@login_required
def pause_order(id):
    order = WorkOrder.query.get_or_404(id)
    data = request.get_json() or {}
    reason = data.get('reason', 'Sin motivo especificado')

    if order.status == WorkOrderStatus.EXECUTION:
        order.status = WorkOrderStatus.PENDING
        
        downtime = DowntimeEvent(
            work_order_id=order.id,
            reason=reason,
            comment=data.get('comment'),
            start_time=datetime.now()
        )
        db.session.add(downtime)
        db.session.commit()
        return jsonify({"message": "Order paused", "status": order.status.value})
        
    elif order.status == WorkOrderStatus.PENDING:
        open_downtime = DowntimeEvent.query.filter_by(
            work_order_id=order.id, 
            end_time=None
        ).order_by(DowntimeEvent.start_time.desc()).first()
        
        if open_downtime and open_downtime.reason == "Automático: Pendiente de justificar":
            open_downtime.reason = reason
            if data.get('comment'):
                open_downtime.comment = data.get('comment')
            db.session.commit()
            return jsonify({"message": "Downtime justified", "status": order.status.value})

    return jsonify({"error": "Order must be in EXECUTION to pause or have an automatic pending downtime"}), 400

@orders_bp.route('/<int:id>/finish', methods=['POST'])
@login_required
def finish_order(id):
    order = WorkOrder.query.get_or_404(id)
    data = request.get_json() or {}
    
    if 'produced_quantity' in data:
         order.total_produced = int(data['produced_quantity'])

    if 'sensor_count' in data:
         order.sensor_count = int(data['sensor_count'])
         
    if 'manual_count_modified' in data:
         order.manual_count_modified = bool(data['manual_count_modified'])

    order.status = WorkOrderStatus.FINISHED
    order.end_time = datetime.now()
    
    downtime = DowntimeEvent.query.filter_by(work_order_id=order.id, end_time=None).first()
    if downtime:
        downtime.end_time = order.end_time
        downtime.duration_seconds = int((downtime.end_time - downtime.start_time).total_seconds())

    db.session.commit()
    return jsonify({"message": "Order finished", "status": order.status.value})

@orders_bp.route('/<int:id>/status_realtime', methods=['GET'])
@login_required
def status_realtime(id):
    order = WorkOrder.query.get_or_404(id)
    
    response = {
        "status": order.status.name,
        "total_produced": order.total_produced
    }
    
    if order.status == WorkOrderStatus.PENDING:
        needs_justify = DowntimeEvent.query.filter_by(
            work_order_id=order.id, 
            end_time=None,
            reason="Automático: Pendiente de justificar"
        ).first()
        
        if needs_justify:
            response["force_justify"] = True
            
    return jsonify(response)


@orders_bp.route('/<int:id>/changeover/start', methods=['POST'])
@login_required
def start_changeover(id):
    db.session.remove()
    order = WorkOrder.query.get_or_404(id)
    
    if order.status != WorkOrderStatus.PENDING:
         return jsonify({"error": "Order must be PENDING to start changeover"}), 400

    open_event = DowntimeEvent.query.filter_by(work_order_id=order.id, end_time=None).first()
    if open_event:
        return jsonify({"error": "An event is already in progress"}), 400

    event = DowntimeEvent(
        work_order_id=order.id,
        reason="Cambio de Paso",
        start_time=datetime.now()
    )
    db.session.add(event)
    db.session.commit()
    
    return jsonify({"message": "Changeover started", "start_time": event.start_time.isoformat()})

@orders_bp.route('/<int:id>/changeover/stop', methods=['POST'])
@login_required
def stop_changeover(id):
    db.session.remove()
    order = WorkOrder.query.get_or_404(id)
    
    open_event = DowntimeEvent.query.filter_by(work_order_id=order.id, end_time=None).first()
    
    if not open_event:
        return jsonify({"message": "No active changeover found"}), 200
        
    open_event.end_time = datetime.now()
    delta = open_event.end_time - open_event.start_time
    open_event.duration_seconds = int(delta.total_seconds())
    
    db.session.commit()
    
    return jsonify({"message": "Changeover stopped", "duration": open_event.duration_seconds})
