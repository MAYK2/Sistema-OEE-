from app import create_app, db
from app.models.user import User
from sqlalchemy import inspect

app = create_app()

with app.app_context():
    print("--- Inspecting Database ---")
    inspector = inspect(db.engine)
    if 'users' in inspector.get_table_names():
        print("✅ Table 'users' exists.")
        columns = [c['name'] for c in inspector.get_columns('users')]
        print(f"   Columns: {columns}")
        
        required_columns = ['id', 'username', 'password_hash']
        missing = [col for col in required_columns if col not in columns]
        
        if missing:
            print(f"❌ MISSING COLUMNS: {missing}")
        else:
            print("✅ All required columns are present.")
            
            # Check for admin user
            admin = User.query.filter_by(username='admin').first()
            if admin:
                print(f"✅ Admin user found: {admin.username} (ID: {admin.id})")
            else:
                print("⚠️ Admin user NOT found.")
                # Attempt to create if structure is okay
                try:
                    admin = User(username='admin')
                    admin.set_password('admin')
                    db.session.add(admin)
                    db.session.commit()
                    print("   + Created 'admin' user successfully.")
                except Exception as e:
                    print(f"   ❌ Failed to create admin user: {e}")
    else:
        print("❌ Table 'users' DOES NOT EXIST (according to SQLAlchemy inspector).")
        print("   Attempting to create it now...")
        try:
            db.create_all()
            print("   ✅ db.create_all() executed.")
        except Exception as e:
            print(f"   ❌ db.create_all() failed: {e}")
