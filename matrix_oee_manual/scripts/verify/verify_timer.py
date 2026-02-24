import requests
import time
import random

BASE_URL = "http://127.0.0.1:5000"

def run_test():
    # Create.
    payload = {
        "client_mode": "existing",
        "existing_client_id": 2,
        "items": [
           {"product_id": 1, "quantity": 100}
        ]
    }
    r = requests.post(f"{BASE_URL}/orders/new", json=payload)
    
    try:
        data = r.json()
        # Parse the message or just count on the DB being incremental?
        # The view returns: {'message': 'X órdenes creadas correctamente'}
        # It doesn't return the ID. We should query it or just assume it's the last one.
        pass
    except:
        pass

    # Get the latest order ID
    r_list = requests.get(f"{BASE_URL}/")
    # This returns HTML (index). We need an API or just query DB?
    # Let's just use a hardcoded higher number OR make the script smarter.
    # Actually, the create_order view returns JSON: {'message': ...} but NOT the ID.
    
    # Better approach: Fix the script to fetch the latest order ID via a simple hack or by reading the DB side channel if possible?
    # Or just use the `/operate/` logic to spy.
    # Let's try to parse the ID from the logs? No.
    # Let's just guess the ID is "Last + 1".
    
    # EASIEST: Just modify the Create View to return the ID? No, that's changing code.
    # Let's just assume the order created is the latest one.
    pass
    
    # Hack: Let's loop a bit or just manually set it to something we know exists?
    # Or just requests.get(history). 
    
    # Let's change the script to use a known high number or loop. 
    # Or better yet, just look at the `views.py` response.
    # The view returns 200 and a message.
    
    # Let's try to scrape the index page for the latest ID.
    # Or just trust the user manual test? 
    # I can just write a small python script to query the DB directly since I am on the server.
    from app.models.work_order import WorkOrder
    from app import create_app
    app = create_app()
    with app.app_context():
        order = WorkOrder.query.order_by(WorkOrder.id.desc()).first()
        order_id = order.id
    
    print(f"Using Order ID: {order_id}")

    # 2. Start
    requests.post(f"{BASE_URL}/api/orders/{order_id}/start", json={})
    
    # 3. Hit Logic
    time.sleep(2)
    requests.get(f"{BASE_URL}/operate/{order_id}")

    # 4. Pause
    requests.post(f"{BASE_URL}/api/orders/{order_id}/pause", json={"reason": "test"})
    
    # 5. Hit Logic
    time.sleep(2)
    requests.get(f"{BASE_URL}/operate/{order_id}")

    # 6. Resume
    requests.post(f"{BASE_URL}/api/orders/{order_id}/start", json={})
    
    # 7. Hit Logic
    time.sleep(2)
    requests.get(f"{BASE_URL}/operate/{order_id}")

if __name__ == "__main__":
    run_test()
