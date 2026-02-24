import getpass
from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash

app = create_app()

def gestionar_usuario():
    with app.app_context():
        print("\n=== GESTOR DE USUARIOS OEE ===")
        print("Este script sirve para CREAR usuarios nuevos o CAMBIAR contraseñas.")
        print("-------------------------------------------------------------")
        
        # 1. Pedir nombre de usuario
        username = input("👤 Ingrese el nombre de usuario (ej: supervisor, operario1): ").strip()
        
        if not username:
            print("❌ Error: El nombre no puede estar vacío.")
            return

        # 2. Buscar en la base de datos
        usuario = User.query.filter_by(username=username).first()
        es_nuevo = False

        if usuario:
            print(f"✅ El usuario '{username}' YA EXISTE (ID: {usuario.id}).")
            print("   -> Se actualizará su contraseña.")
        else:
            print(f"🆕 El usuario '{username}' NO EXISTE.")
            print("   -> Se creará un usuario nuevo.")
            es_nuevo = True

        # 3. Pedir contraseña segura
        password = getpass.getpass(f"🔑 Ingrese la contraseña para '{username}': ")
        confirmacion = getpass.getpass("🔁 Confirme la contraseña: ")

        if password != confirmacion:
            print("❌ Error: Las contraseñas no coinciden.")
            return
        
        if not password:
             print("❌ Error: La contraseña no puede estar vacía.")
             return

        # 4. Pedir Rol
        print("\nSeleccione el Rol:")
        print("1. Admin (Acceso total)")
        print("2. Operario (Solo ver/ejecutar OTs)")
        role_choice = input("Opción (1/2) [Defecto: Operario]: ").strip()
        
        role = 'operator'
        if role_choice == '1':
            role = 'admin'
        
        print(f"   -> Rol seleccionado: {role.upper()}")

        # 5. Encriptar contraseña y Guardar
        password_hash_nuevo = generate_password_hash(password)

        if es_nuevo:
            # CREAR USUARIO NUEVO
            nuevo_usuario = User(username=username, password_hash=password_hash_nuevo, role=role)
            db.session.add(nuevo_usuario)
            accion = "creado"
        else:
            # ACTUALIZAR EXISTENTE
            usuario.password_hash = password_hash_nuevo
            usuario.role = role
            accion = "actualizado"

        # 5. Guardar cambios
        try:
            db.session.commit()
            print(f"\n🎉 ¡ÉXITO! El usuario '{username}' ha sido {accion} correctamente.")
        except Exception as e:
            db.session.rollback()
            print(f"\n❌ Error de base de datos: {e}")

if __name__ == "__main__":
    gestionar_usuario()