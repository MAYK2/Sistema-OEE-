from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.work_order import WorkOrder, WorkOrderStatus
from app.models.downtime import DowntimeEvent, DowntimeStage, DowntimeType
from datetime import datetime

orders_bp = Blueprint('orders', __name__)

@orders_bp.route('/', methods=['POST'])
def create_order():
    data = request.get_json()
    
    # Validation (Basic)
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

# @orders_bp.route('/<int:id>/start', methods=['POST'])
# def start_order(id):
#     order = WorkOrder.query.get_or_404(id)
#     data = request.get_json()
    
#     if order.status != WorkOrderStatus.PENDING:
#         return jsonify({"error": "Order must be PENDING to start"}), 400
        
#     order.status = WorkOrderStatus.EXECUTION
#     order.start_time_real = datetime.utcnow()
#     order.operator_count = data.get('operator_count', 1)
    
#     db.session.commit()
    
#     return jsonify({
#         "message": "Order started",
#         "status": order.status.value,
#         "start_time": order.start_time_real.isoformat()
#     }), 200

# @orders_bp.route('/<int:id>/downtime', methods=['POST'])
# def register_downtime(id):
#     order = WorkOrder.query.get_or_404(id)
#     data = request.get_json()
    
#     # Map strings to Enums
#     stage_map = {
#         'preparacion': DowntimeStage.PREPARATION,
#         'ejecucion': DowntimeStage.EXECUTION
#     }
    
#     type_map = {
#         'productivo': DowntimeType.PRODUCTIVE,
#         'improductivo': DowntimeType.UNPRODUCTIVE
#     }
    
#     try:
#         stage_enum = stage_map.get(data.get('stage', '').lower())
#         type_enum = type_map.get(data.get('type', '').lower())
        
#         if not stage_enum or not type_enum:
#             return jsonify({"error": "Invalid stage or type"}), 400
            
#         downtime = DowntimeEvent(
#             work_order_id=order.id,
#             stage=stage_enum,
#             type=type_enum,
#             reason=data.get('reason', 'Unknown'),
#             duration_minutes=int(data.get('duration_minutes', 0))
#         )
        
#         db.session.add(downtime)
#         db.session.commit()
        
#         return jsonify({"message": "Downtime registered", "id": downtime.id}), 201
        
#     except ValueError:
#         return jsonify({"error": "Invalid data format"}), 400

# @orders_bp.route('/<int:id>/stop', methods=['POST'])
# def stop_order(id):
#     order = WorkOrder.query.get_or_404(id)
#     data = request.get_json()
    
#     if order.status != WorkOrderStatus.EXECUTION:
#         return jsonify({"error": "Order must be in EXECUTION to stop"}), 400
        
#     order.status = WorkOrderStatus.FINISHED
#     order.end_time_real = datetime.utcnow()
#     order.total_produced = data.get('total_produced', 0)
#     order.total_defective = data.get('total_defective', 0)
    
#     db.session.commit()
    
#     return jsonify({
#         "message": "Order finished",
#         "status": order.status.value,
#         "end_time": order.end_time_real.isoformat()
#     }), 200
