import requests
from app import create_app
from app.models.line import Line
from app.models.work_order import WorkOrder
from datetime import datetime, timedelta

app = create_app()

def verify_oee_logic():
    with app.app_context():
        # Get Line 1
        line = Line.query.get(1)
        if not line:
            print("FAILED: Line 1 not found")
            return
            
        print(f"--- Verifying OEE Logic for {line.name} ---")
        
        # Simulate overlaps: 
        # Check current OEE
        # We can't unit test the inner function of a view easily without refactoring.
        # But we can check the /dashboard response via test client.
        
        with app.test_client() as client:
             # Login
             client.post('/login', data={'username': 'operario', 'password': 'password'}, follow_redirects=True)
             
             resp = client.get('/dashboard')
             if resp.status_code != 200:
                 print(f"FAILED: Dashboard returned {resp.status_code}")
                 print(resp.data.decode()[:500])
                 return
             
             content = resp.data.decode()
             print("PASSED: Dashboard loaded")
             
             # Check for OEE > 100% (simple text search for now)
             # "166%" was the bug.
             # We should look for "Disponibilidad" and values.
             # But 'lines_data' context is not easily accessible from outside unless we parse HTML or use a stronger test.
             
             if "Semana" in content and "Mes" in content:
                 print("PASSED: Found Weekly/Monthly labels")
             else:
                 print("FAILED: Weekly/Monthly labels not found")
                 
             # Check for "166%" or anything > 100% in the OEE text
             import re
             matches = re.findall(r'(\d+(?:\.\d+)?)%', content)
             for m in matches:
                 try:
                     val = float(m)
                     if val > 100:
                         print(f"WARNING: Found percentage > 100%: {val}%")
                         # Note: It might be possible if we didn't clamp? 
                         # But our logic has min(100, ...).
                         # If found, it's a fail.
                         return
                 except:
                     pass
             
             print("PASSED: No percentages > 100% found")

if __name__ == "__main__":
    verify_oee_logic()
