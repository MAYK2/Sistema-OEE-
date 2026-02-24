from app import create_app, db
from app.models.line import Line
from app.models.product import Product
from app.models.work_order import WorkOrder, WorkOrderStatus
from app.models.downtime import DowntimeEvent, DowntimeStage, DowntimeType
import os

# Use SQLite for testing
class TestConfig:
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = 'test'

app = create_app(TestConfig)

with app.app_context():
    try:
        print("Creating tables...")
        db.create_all()
        print("Tables created.")

        print("Creating test data...")
        line1 = Line(name="Linea 1 - Agua")
        db.session.add(line1)
        db.session.commit()

        prod1 = Product(name="Bidon 20L", line_id=line1.id, theoretical_cycle_seconds=12.5)
        db.session.add(prod1)
        db.session.commit()

        ot1 = WorkOrder(
            ot_number="OT-2023-001",
            client_name="Cliente Test",
            product_id=prod1.id,
            status=WorkOrderStatus.PENDING,
            operator_count=3
        )
        db.session.add(ot1)
        db.session.commit()

        dt1 = DowntimeEvent(
            work_order_id=ot1.id,
            stage=DowntimeStage.EXECUTION,
            type=DowntimeType.UNPRODUCTIVE,
            reason="Falla Sensor",
            duration_minutes=15
        )
        db.session.add(dt1)
        db.session.commit()

        print("Verification Successful!")
        print(f"Verified: {ot1} with {len(ot1.downtime_events)} downtime events.")

    except Exception as e:
        print(f"Verification FAILED: {e}")
