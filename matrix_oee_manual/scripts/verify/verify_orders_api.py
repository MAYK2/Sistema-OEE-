import unittest
import json
from app import create_app, db
from app.models.work_order import WorkOrder, WorkOrderStatus
from app.models.product import Product
from app.models.line import Line

class TestOrdersAPI(unittest.TestCase):
    def setUp(self):
        class TestConfig:
            SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
            SQLALCHEMY_TRACK_MODIFICATIONS = False
            SECRET_KEY = 'test'
            TESTING = True

        self.app = create_app(TestConfig)
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Create prerequisites
        line = Line(name="Linea Test")
        db.session.add(line)
        db.session.commit()
        
        self.product = Product(name="Producto Test", line_id=line.id, theoretical_cycle_seconds=10)
        db.session.add(self.product)
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_full_order_flow(self):
        # 1. Create Order
        res = self.client.post('/api/orders/', json={
            "ot_number": "OT-FLOW-001",
            "client_name": "Cliente Flow",
            "product_id": self.product.id
        })
        self.assertEqual(res.status_code, 201)
        order_id = res.json['id']
        self.assertEqual(res.json['status'], WorkOrderStatus.PENDING.value)

        # 2. Start Order
        res = self.client.post(f'/api/orders/{order_id}/start', json={"operator_count": 5})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['status'], WorkOrderStatus.EXECUTION.value)

        # 3. Register Downtime
        res = self.client.post(f'/api/orders/{order_id}/downtime', json={
            "stage": "ejecucion",
            "type": "improductivo",
            "reason": "Test Failure",
            "duration_minutes": 10
        })
        self.assertEqual(res.status_code, 201)

        # 4. Stop Order
        res = self.client.post(f'/api/orders/{order_id}/stop', json={
            "total_produced": 500,
            "total_defective": 2
        })
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json['status'], WorkOrderStatus.FINISHED.value)

if __name__ == '__main__':
    unittest.main()
