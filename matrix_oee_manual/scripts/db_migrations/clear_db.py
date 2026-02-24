from app import create_app, db
from app.models.work_order import WorkOrder
from app.models.downtime import DowntimeEvent
from app.models.client import Client
from sqlalchemy import text

app = create_app()
app.app_context().push()

def clear_data():
    print("--- STARTING DATABASE CLEANUP ---")
    
    # 1. Delete DowntimeEvent (Child of WorkOrder)
    num_downtimes = DowntimeEvent.query.delete()
    print(f"Deleted {num_downtimes} Downtime Events.")
    
    # 2. Delete WorkOrder (Child of Client, Parent of Downtime)
    num_orders = WorkOrder.query.delete()
    print(f"Deleted {num_orders} Work Orders.")
    
    # 3. Delete Client (Parent of WorkOrder)
    num_clients = Client.query.delete()
    print(f"Deleted {num_clients} Clients.")
    
    # Commit changes
    db.session.commit()
    
    print("--- CLEANUP COMPLETE ---")
    print("Products and System Configuration have been preserved.")

if __name__ == '__main__':
    try:
        clear_data()
    except Exception as e:
        print(f"Error during cleanup: {e}")
        db.session.rollback()
