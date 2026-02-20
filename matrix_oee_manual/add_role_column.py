from app import create_app, db
from sqlalchemy import text

app = create_app()

def add_role_column():
    """
    Agrega la columna 'role' a la tabla 'users' si no existe.
    Establece 'admin' como valor por defecto para usuarios existentes.
    """
    with app.app_context():
        print("Iniciando migración de base de datos...")
        
        # 1. Verificar si la columna ya existe
        inspector = db.inspect(db.engine)
        columns = [col['name'] for col in inspector.get_columns('users')]
        
        if 'role' in columns:
            print("✅ La columna 'role' ya existe en la tabla 'users'.")
            return

        # 2. Agregar la columna
        try:
            # SQLite no soporta ADD COLUMN con DEFAULT en una sola transacción compleja a veces, 
            # pero para strings simples suele funcionar. 
            # Sin embargo, SQLAlchemy recomienda usar migraciones reales (Alembic).
            # Aquí usaremos SQL directo para simplicidad dado que es un proyecto manual.
            
            # Nota: 'server_default' en SQLAlchemy no siempre aplica en SQLite retroactivamente de la misma forma.
            # Haremos: ADD COLUMN role VARCHAR(20) DEFAULT 'operator'
            
            with db.engine.connect() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(20) DEFAULT 'operator'"))
                
                # 3. Actualizar usuarios existentes a 'admin' para no bloquear acceso
                conn.execute(text("UPDATE users SET role = 'admin'"))
                
                conn.commit()
                
            print("🎉 Columna 'role' agregada correctamente.")
            print("🔄 Todos los usuarios existentes han sido seteados como 'admin'.")
            
        except Exception as e:
            print(f"❌ Error durante la migración: {e}")

if __name__ == "__main__":
    add_role_column()
