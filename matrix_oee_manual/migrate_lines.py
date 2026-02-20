from app import create_app, db
from app.models.line import Line
from sqlalchemy import text
import datetime

app = create_app()

def migrate():
    with app.app_context():
        with db.engine.connect() as conn:
            # Quote table name `lines`
            
            # Add shift_start
            try:
                conn.execute(text("ALTER TABLE `lines` ADD COLUMN shift_start TIME NULL"))
                print("Added shift_start column")
            except Exception as e:
                print(f"Skipping shift_start: {e}")

            # Add shift_end
            try:
                conn.execute(text("ALTER TABLE `lines` ADD COLUMN shift_end TIME NULL"))
                print("Added shift_end column")
            except Exception as e:
                print(f"Skipping shift_end: {e}")
            
            conn.commit()
        
        # Ensure at least one Line exists with default hours
        if Line.query.count() == 0:
            print("Creating default Line 1...")
            default_line = Line(
                name="Línea 1",
                shift_start=datetime.time(8, 0),
                shift_end=datetime.time(17, 0)
            )
            db.session.add(default_line)
            db.session.commit()
            print("Default Line created.")
        else:
             # Update existing lines to have default if null
             lines = Line.query.filter(Line.shift_start == None).all()
             for l in lines:
                 l.shift_start = datetime.time(8, 0)
                 l.shift_end = datetime.time(17, 0)
                 print(f"Updated Line {l.name} with defaults.")
             db.session.commit()

if __name__ == "__main__":
    migrate()
