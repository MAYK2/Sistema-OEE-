from app import create_app
from app.models.work_order import WorkOrder
app = create_app()
with app.app_context():
    order = WorkOrder.query.get(65)
    print("Order exists?", order is not None)
    try:
        WorkOrder.query.get_or_404(65)
        print("get_or_404 succeeded")
    except Exception as e:
        print("get_or_404 failed with:", type(e))
