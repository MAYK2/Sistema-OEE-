from app import create_app
from app.models.work_order import WorkOrder
from datetime import datetime

app = create_app()
with app.app_context():
    count = WorkOrder.query.count()
    print(f"Total Count: {count}")
    
    year = datetime.now().year
    last_order = WorkOrder.query.filter(WorkOrder.ot_number.like(f'OT-{year}-%'))                                .order_by(WorkOrder.id.desc())                                .first()
    
    print(f"Last Order Found: {last_order.ot_number if last_order else 'None'}")
    
    last_seq = 0
    if last_order:
        try:
            last_seq = int(last_order.ot_number.split('-')[-1])
        except ValueError:
            pass
            
    print(f"Derived Last Seq: {last_seq}")
    next_ot = f"OT-{year}-{last_seq + 1:04d}"
    print(f"Proposed Next OT: {next_ot}")
    
    # Verify if this proposed OT exists
    exists = WorkOrder.query.filter_by(ot_number=next_ot).first()
    if exists:
        print(f"CRITICAL: Proposed OT {next_ot} ALREADY EXISTS!")
    else:
        print(f"SUCCESS: Proposed OT {next_ot} is available.")
