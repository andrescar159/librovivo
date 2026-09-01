"""
Configuracion de LibroVivo - Sistema de Gestion Bibliotecaria
"""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuracion base"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'librovivo-secret-key-2026'
    
    # Configuracion MySQL (XAMPP)
    MYSQL_HOST = os.environ.get('MYSQL_HOST') or 'localhost'
    MYSQL_PORT = int(os.environ.get('MYSQL_PORT') or 3306)
    MYSQL_USER = os.environ.get('MYSQL_USER') or 'root'
    MYSQL_PASSWORD = os.environ.get('MYSQL_PASSWORD') or ''
    MYSQL_DB = os.environ.get('MYSQL_DB') or 'librovivo'
    
    # Configuracion de la aplicacion
    APP_NAME = 'LibroVivo'
    APP_VERSION = '1.0.0'
    
    # Horario de atencion de la biblioteca
    HORARIO_APERTURA = 7    # 7:00 AM
    HORARIO_CIERRE = 17     # 5:00 PM
    
    # Reglas de prestamo
    MAX_PRESTAMOS_ESTUDIANTE = 3
    DIAS_PRESTAMO = 15
    MAX_RENOVACIONES = 3
    DIAS_EXTENSION_BIBLIOTECARIO = 2
    
    # Reglas de multas (pesos colombianos)
    MULTA_POR_DIA = 500
    DIAS_LIMITE_MULTA = 10
    MULTA_MAXIMA = 7000
    
    # Reglas de reservas
    MAX_RESERVAS_ACTIVAS = 2
    DIAS_RESERVA = 3
    
    # Configuracion de correo (para notificaciones)
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.gmail.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', '1', 'yes']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or ''
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or ''
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER') or 'librovivo@colegio.edu'
    
    # Configuracion de archivos
    UPLOAD_FOLDER_PERFILES = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'uploads', 'perfiles')
    UPLOAD_FOLDER_PORTADAS = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'static', 'uploads', 'portadas')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    # Paginacion
    PER_PAGE = 10
    
    # Recordatorio de vencimiento (dias antes)
    DIAS_RECORDATORIO = 2


class DevelopmentConfig(Config):
    """Configuracion de desarrollo"""
    DEBUG = True


class ProductionConfig(Config):
    """Configuracion de produccion"""
    DEBUG = False


config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}