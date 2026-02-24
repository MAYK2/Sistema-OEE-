import os
import sys

# Add root project dir to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from app import create_app
from app.extensions import db
from app.models.work_order import WorkOrder, WorkOrderStatus
from app.models.downtime import DowntimeEvent
from datetime import datetime, timedelta

app = create_app()

def run_tests():
    with app.test_client() as client:
        with app.app_context():
            # Find an active order to make the test realistic, or create one.
            order = WorkOrder.query.filter_by(status=WorkOrderStatus.EXECUTION).first()
            if not order:
                order = WorkOrder.query.filter_by(status=WorkOrderStatus.PENDING).first()
                if order:
                    order.status = WorkOrderStatus.EXECUTION
                    db.session.commit()
            
            if not order:
                print("No pending/execution orders found. Creating a dummy one.")
                from app.models.client import Client
                from app.models.product import Product
                from app.models.line import Line
                
                client_obj = Client.query.first() or Client(name="Test Client", phone="123", email="test@test.com")
                line = Line.query.first() or Line(name="Línea 1")
                db.session.add(client_obj)
                db.session.add(line)
                db.session.commit()
                
                prod = Product.query.first() or Product(name="Test Product", line_id=line.id)
                db.session.add(prod)
                db.session.commit()
                
                order = WorkOrder.query.filter_by(ot_number="OT-TEST-001").first()
                if not order:
                    order = WorkOrder(ot_number="OT-TEST-001", client_id=client_obj.id, product_id=prod.id, status=WorkOrderStatus.EXECUTION)
                    db.session.add(order)
                    db.session.commit()
                else:
                    order.status = WorkOrderStatus.EXECUTION
                    db.session.commit()
            
            print(f"--- TESTING WITH OT: {order.ot_number} (Line: {order.product.line_id}) ---")
            initial_produced = order.total_produced
            
            # --- 1. SIMULATE RUNNING (Count) ---
            print("\n1. Simulating 5 units produced...")
            resp = client.post('/api/iot/telemetria', json={
                "line_id": order.product.line_id,
                "produced_count": 5,
                "machine_status": "running"
            })
            print("Status:", resp.status_code)
            print("Response:", resp.json)
            
            # Refetch to check DB
            order = WorkOrder.query.get(order.id)
            assert order.total_produced == initial_produced + 5
            print("Success! DB updated.", order.total_produced)

            # --- 2. SIMULATE STOP (Auto-Pause) ---
            print("\n2. Simulating Machine Stop (Auto Pause)...")
            past_time_stop = (datetime.now() - timedelta(minutes=10)).isoformat()
            resp = client.post('/api/iot/telemetria', json={
                "line_id": order.product.line_id,
                "produced_count": 0,
                "machine_status": "stopped",
                "timestamp": past_time_stop
            })
            print("Status:", resp.status_code)
            print("Response:", resp.json)
            
            order = WorkOrder.query.get(order.id)
            assert order.status == WorkOrderStatus.PENDING
            
            # Check Downtime
            dt = DowntimeEvent.query.filter_by(work_order_id=order.id, end_time=None).first()
            assert dt is not None
            assert dt.reason == "Automático: Pendiente de justificar"
            print("Success! Order auto-paused and downtime event created.")
            
            # --- 3. SIMULATE RESUME (Auto-Resume) ---
            print("\n3. Simulating Machine Resume (Auto Resume)...")
            past_time_run = (datetime.now() - timedelta(minutes=5)).isoformat()
            resp = client.post('/api/iot/telemetria', json={
                "line_id": order.product.line_id,
                "produced_count": 0,
                "machine_status": "running",
                "timestamp": past_time_run
            })
            print("Status:", resp.status_code)
            print("Response:", resp.json)
            
            order = WorkOrder.query.get(order.id)
            assert order.status == WorkOrderStatus.EXECUTION
            
            # Check Downtime closed
            dt = DowntimeEvent.query.get(dt.id)
            assert dt.end_time is not None
            assert dt.duration_seconds == 300 # 5 minutes difference
            print("Success! Order auto-resumed and downtime closed with exact duration:", dt.duration_seconds)
            print("Test Completed Successfully!")

if __name__ == "__main__":
    run_tests()
