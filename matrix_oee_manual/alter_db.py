from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app()
with app.app_context():
    try:
        db.session.execute(text("ALTER TABLE work_orders ADD COLUMN sensor_count INT DEFAULT 0;"))
        db.session.execute(text("ALTER TABLE work_orders ADD COLUMN manual_count_modified BOOLEAN DEFAULT FALSE;"))
        db.session.commit()
        print("Columns added successfully.")
    except Exception as e:
        print("Error:", e)
