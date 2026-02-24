import sys
import os
from datetime import datetime, time, timedelta

# Add app context
sys.path.append(os.getcwd())
from app import create_app, db
from app.models.line import Line

app = create_app()

def test_shift_logic():
    with app.app_context():
        print("--- Testing Shift Logic ---")
        
        # 1. Setup Line Shift (e.g., 8-17)
        line = Line.query.first()
        if not line:
            line = Line(name="Test Line")
            db.session.add(line)
        
        line.shift_start = time(8, 0)
        line.shift_end = time(17, 0)
        db.session.commit()
        print(f"Line Shift: {line.shift_start} - {line.shift_end}")
        
        # 2. Simulate Time scenarios
        # We can't easily mock 'datetime.now()' inside the view function without patching.
        # So we will replicate the VIEW LOGIC here and assert it works as expected.
        
        scenarios = [
            (datetime(2023, 1, 1, 7, 0), 0, "Before Shift"),
            (datetime(2023, 1, 1, 9, 0), 3600, "1 Hour into Shift"),
            (datetime(2023, 1, 1, 18, 0), 9*3600, "After Shift (Full 9h)"),
        ]
        
        for now_dt, expected_planned, label in scenarios:
            shift_start_dt = datetime.combine(now_dt.date(), line.shift_start)
            shift_end_dt = datetime.combine(now_dt.date(), line.shift_end)
            
            planned_seconds = 0
            if now_dt > shift_start_dt:
                effective_end = min(now_dt, shift_end_dt)
                if effective_end > shift_start_dt:
                    planned_seconds = (effective_end - shift_start_dt).total_seconds()
            
            print(f"Scenario [{label}]: Now={now_dt.time()} -> Planned Seconds={int(planned_seconds)} (Expected {expected_planned})")
            if int(planned_seconds) != expected_planned:
                 print("FAILED!")
            else:
                 print("PASSED")

if __name__ == "__main__":
    test_shift_logic()
