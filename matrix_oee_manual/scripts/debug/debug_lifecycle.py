import time
from datetime import datetime, timedelta
from app import create_app, db
from app.models.work_order import WorkOrder, WorkOrderStatus
from app.models.product import Product
from app.models.client import Client
from app.models.downtime import DowntimeEvent

# Simulation utils
def log(msg):
    print(f"[{datetime.now().strftime('%H:%M:%S')}] {msg}")

def simulate():
    app = create_app()
    with app.app_context():
        log("--- Starting Simulation ---")
        
        # 1. Setup Data
        client = Client.query.first()
        product = Product.query.first() # Bidon 20L (45s cycle)
        
        # Cleanup
        DowntimeEvent.query.delete()
        WorkOrder.query.delete()
        db.session.commit()
        
        # 2. Create Order
        order = WorkOrder(
            ot_number="TEST-001",
            client_id=client.id,
            product_id=product.id,
            planned_quantity=10,
            status=WorkOrderStatus.PENDING
        )
        db.session.add(order)
        db.session.commit()
        log(f"Order Created: {order.id}. Status: {order.status}")
        
        # 3. START Order
        order.status = WorkOrderStatus.EXECUTION
        order.start_time = datetime.now()
        db.session.commit()
        log(">>> Order STARTED.")
        
        time.sleep(2) 
        
        # 4. PAUSE Order
        # Simulate /api/orders/<id>/pause
        log(">>> Pausing Order...")
        order.status = WorkOrderStatus.PENDING
        downtime = DowntimeEvent(
            work_order_id=order.id,
            reason="Test Pause",
            start_time=datetime.now()
        )
        db.session.add(downtime)
        db.session.commit()
        
        time.sleep(2)
        
        # Check calculation during PAUSE
        now_time = datetime.now()
        total_duration = (now_time - order.start_time).total_seconds()
        downtimes = DowntimeEvent.query.filter_by(work_order_id=order.id).all()
        total_dt = sum(d.duration_seconds for d in downtimes if d.duration_seconds)
        
        current_pause = next((d for d in downtimes if d.end_time is None), None)
        curr_pause_dur = (now_time - current_pause.start_time).total_seconds() if current_pause else 0
        
        elapsed = int(max(0, total_duration - total_dt - curr_pause_dur))
        log(f"   [IN PAUSE] TotalDur: {total_duration:.2f}, ClosedDT: {total_dt}, CurrPause: {curr_pause_dur:.2f} => Elapsed: {elapsed}")
        
        # 5. RESUME Order
        # Simulate /api/orders/<id>/start logic
        log(">>> Resuming Order...")
        downtime = DowntimeEvent.query.filter_by(work_order_id=order.id, end_time=None).first()
        if downtime:
            downtime.end_time = datetime.now()
            d = downtime.end_time - downtime.start_time
            downtime.duration_seconds = int(d.total_seconds())
        
        order.status = WorkOrderStatus.EXECUTION
        if not order.start_time: # Should be false
             order.start_time = datetime.now()
        db.session.commit()
        
        time.sleep(2)
        
        # Check calculation after RESUME
        now_time = datetime.now()
        total_duration = (now_time - order.start_time).total_seconds()
        downtimes = DowntimeEvent.query.filter_by(work_order_id=order.id).all()
        total_dt = sum(d.duration_seconds for d in downtimes if d.duration_seconds)
        current_pause = next((d for d in downtimes if d.end_time is None), None) # Should be None
        curr_pause_dur = 0
        
        elapsed = int(max(0, total_duration - total_dt - curr_pause_dur))
        log(f"   [RUNNING] TotalDur: {total_duration:.2f}, ClosedDT: {total_dt}, CurrPause: {curr_pause_dur:.2f} => Elapsed: {elapsed}")
        
        # 6. FINISH Order
        log(">>> Finishing Order...")
        order.total_produced = 5
        order.status = WorkOrderStatus.FINISHED
        order.end_time = datetime.now()
        db.session.commit()
        
        # Check KPIs
        log(f"   KPIs -> Performance: {order.performance}%, OEE: {order.oee}%")
        log(f"   RunTime: {order.run_time_seconds}, TotalTime: {order.total_time_seconds}")


if __name__ == "__main__":
    simulate()
