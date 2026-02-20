from app import create_app, db
from app.models.user import User

app = create_app()

with app.app_context():
    print("--- DEBUG USER 'operario' ---")
    u = User.query.filter_by(username='operario').first()
    if u:
        print(f"ID: {u.id}")
        print(f"Username: '{u.username}'")
        print(f"Role (Raw DB): '{u.role}'")
        print(f"is_admin (Property): {u.is_admin}")
        print(f"is_operator (Property): {u.is_operator}")
    else:
        print("User 'operario' not found!")

    print("\n--- CHECKING ALL USERS ---")
    users = User.query.all()
    for user in users:
         print(f"User: {user.username} | Role: '{user.role}' | is_admin: {user.is_admin}")
