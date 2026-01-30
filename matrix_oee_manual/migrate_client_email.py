from app import create_app
from app.extensions import db
from sqlalchemy import text

app = create_app()

with app.app_context():
    try:
        # Check if column exists first to be safe
        with db.engine.connect() as conn:
            result = conn.execute(text("SHOW COLUMNS FROM clients LIKE 'email'"))
            if result.fetchone():
                print("Column 'email' already exists in 'clients' table.")
            else:
                print("Adding 'email' column to 'clients' table...")
                conn.execute(text("ALTER TABLE clients ADD COLUMN email VARCHAR(120)"))
                conn.commit()
                print("Column added successfully.")
    except Exception as e:
        print(f"Error during migration: {e}")
