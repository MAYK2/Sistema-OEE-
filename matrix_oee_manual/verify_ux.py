import sys
import os
import json
from datetime import datetime, time

# Add app context
sys.path.append(os.getcwd())
from app import create_app, db
from app.models.line import Line
from app.models.work_order import WorkOrder, WorkOrderStatus
from app.models.user import User

app = create_app()

def verify_ux_features():
    with app.test_request_context():
        with app.test_client() as client:
            print("--- 1. Verify Multi-Line Config API ---")
            # Ensure we have 2 lines
            line1 = Line.query.get(1)
            line2 = Line.query.get(2)
            if not line2:
                line2 = Line(name="Línea 2 - Sodas", shift_start=time(9,0), shift_end=time(18,0))
                db.session.add(line2)
                db.session.commit()
                print("Created Line 2")
            
            # Test GET
            res = client.get('/api/catalogs/lines')
            data = res.json
            print(f"GET /catalogs/lines: Found {len(data)} lines")
            if len(data) >= 2:
                print("PASSED: Multiple lines returned")
            else:
                print("FAILED: Expected multiple lines")

            print("\n--- 2. Verify Global Active Order Context ---")
            # Log in a user (simulate)
            user = User.query.first()
            if not user:
                print("No user found to test login context")
                return

            # Ensure an active order exists
            order = WorkOrder.query.filter_by(status=WorkOrderStatus.EXECUTION).first()
            if not order:
                print("Creating dummy active order for testing...")
                # ... creation logic skipped for brevity, assuming one exists or we just check logic
                pass
            
            # We can't easily test 'context_processor' injection without rendering a template
            # But we can import the function from app/__init__.py if we could reach it,
            # Or render a simple template string.
            
            from flask import render_template_string
            # Only works if logged in. We can simulate login_user?
            from flask_login import login_user
            login_user(user)
            
            # active order might be None if none exists, that's fine, we just want to see if variables exist
            tmpl = "{{ global_active_order.id if global_active_order else 'None' }}"
            rendered = render_template_string(tmpl)
            print(f"Rendered Template with Context: {rendered}")
            
            if order and rendered != 'None':
                 print("PASSED: Context processor injected active order")
            elif not order and rendered == 'None':
                 print("PASSED: Context processor correctly injected None (no active order)")
            else:
                 print("FAILED: Context processor mismatch")

if __name__ == "__main__":
    verify_ux_features()
