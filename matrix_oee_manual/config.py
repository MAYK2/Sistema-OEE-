import os

class Config:
    # Configuración de conexión a MariaDB
    # Usuario: matrix_user
    # Contraseña: tu_password
    # Base de datos: matrix_oee_db
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://matrix_user:tu_password@localhost/matrix_oee_db'
    
    # Desactivar el rastreo de modificaciones para ahorrar memoria
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Clave secreta para seguridad de sesiones (cámbiala en producción)
    SECRET_KEY = 'dev_key_matrix_electronic'