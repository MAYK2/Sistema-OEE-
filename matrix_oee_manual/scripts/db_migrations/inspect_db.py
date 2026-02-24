from app import create_app, db
from sqlalchemy import text

app = create_app()

def inspect():
    with app.app_context():
        with db.engine.connect() as conn:
            # Check tables
            print("--- Tables ---")
            result = conn.execute(text("SHOW TABLES"))
            for row in result:
                print(row)
            
            # Check lines table columns
            print("\n--- Columns in 'lines' ---")
            try:
                result = conn.execute(text("DESCRIBE lines"))
                for row in result:
                    print(row)
            except Exception as e:
                print(f"Error describing lines: {e}")

if __name__ == "__main__":
    inspect()
