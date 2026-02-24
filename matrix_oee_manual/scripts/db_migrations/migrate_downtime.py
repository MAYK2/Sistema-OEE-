from app import create_app, db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        # Check if column exists first (to avoid error if re-run)
        with db.engine.connect() as conn:
            conn.execute(text("ALTER TABLE downtime_events ADD COLUMN comment VARCHAR(500) NULL;"))
            print("Successfully added 'comment' column to downtime_events.")
            conn.commit()
    except Exception as e:
        print(f"Migration failed (might already exist): {e}")
