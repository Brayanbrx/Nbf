"""
Configuración de la aplicación Flask.
Soporta desarrollo, testing y producción.
"""

import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()


class BaseConfig:
    """Configuración base compartida."""
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-insecure-key-change-in-production')
    DEBUG = False
    TESTING = False
    
    # Sesiones
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 7 * 24 * 60 * 60  # 7 días
    
    # SQLAlchemy
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # ===== RENDIMIENTO Y CACHING =====
    
    # Flask-Compress: Compresión Gzip automática
    COMPRESS_LEVEL = 6  # 1-9, 6 es buen balance
    COMPRESS_MIN_SIZE = 500  # Comprimir si > 500 bytes
    COMPRESS_MIMETYPES = [
        'text/html', 'text/css', 'text/xml', 'text/plain',
        'application/json', 'application/javascript'
    ]
    
    # Flask-Caching: Configuración
    CACHE_TYPE = 'simple'  # 'simple' en dev, 'redis' en prod
    CACHE_DEFAULT_TIMEOUT = 300  # 5 minutos default
    
    # HTTP Cache Headers
    SEND_FILE_MAX_AGE_DEFAULT = 31536000  # 1 año para static files
    
    # SQLAlchemy Query Optimization
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_recycle': 3600,  # Reciclar conexiones cada 1 hora
        'pool_pre_ping': True,  # Verificar conexión antes de usar
        # connect_args vacío para pymssql (no acepta check_same_thread ni timeout)
        'connect_args': {}
    }


class DevelopmentConfig(BaseConfig):
    """Configuración para desarrollo local."""
    
    DEBUG = True
    SESSION_COOKIE_SECURE = False
    SQLALCHEMY_ECHO = False
    
    # Construir URL de BD desde variables de entorno
    db_server = os.getenv('DB_SERVER', 'localhost')
    db_port = os.getenv('DB_PORT', '1433')
    db_name = os.getenv('DB_NAME', 'NBF_Listados')
    db_user = os.getenv('DB_USER', 'sa')
    db_password = os.getenv('DB_PASSWORD', '')
    
    # Construcción de URI de SQLAlchemy para SQL Server con pymssql (sin ODBC)
    quoted_password = db_password.replace('@', '%40').replace(';', '%3B')
    SQLALCHEMY_DATABASE_URI = (
        f"mssql+pymssql://{db_user}:{quoted_password}@{db_server}:{db_port}/{db_name}"
    )
    print(f"[DEV] Conectando a: {db_server}:{db_port}/{db_name} como {db_user}")


class ProductionConfig(BaseConfig):
    """Configuración para producción (Render)."""
    
    DEBUG = False
    SESSION_COOKIE_SECURE = True
    
    # Intentar usar DATABASE_URL (de Render/Somee) si existe
    # Si no, construir desde variables individuales
    database_url = os.getenv('DATABASE_URL')
    
    if database_url:
        SQLALCHEMY_DATABASE_URI = database_url
    else:
        # Fallback a construcción manual
        # En producción (Render), usar pymssql (sin dependencias ODBC)
        db_server = os.getenv('DB_SERVER')
        db_port = os.getenv('DB_PORT', '1433')
        db_name = os.getenv('DB_NAME')
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')
        
        if db_server and db_name and db_user and db_password:
            quoted_password = db_password.replace('@', '%40').replace(';', '%3B')
            SQLALCHEMY_DATABASE_URI = (
                f"mssql+pymssql://{db_user}:{quoted_password}@{db_server}:{db_port}/{db_name}"
            )
            print(f"[PROD] Conectando a: {db_server}:{db_port}/{db_name} como {db_user}")
        else:
            missing = []
            if not db_server: missing.append("DB_SERVER")
            if not db_name: missing.append("DB_NAME")
            if not db_user: missing.append("DB_USER")
            if not db_password: missing.append("DB_PASSWORD")
            raise ValueError(
                f"Producción: Faltan variables de BD: {', '.join(missing)}. "
                f"Configúralas en el Dashboard de Render (Environment variables)."
            )


class TestingConfig(BaseConfig):
    """Configuración para testing."""
    
    DEBUG = True
    TESTING = True
    
    # BD en memoria para tests (SQLite)
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    WTF_CSRF_ENABLED = False


# Seleccionar configuración según entorno
def get_config():
    """Obtener la clase de configuración apropiada."""
    env = os.getenv('FLASK_ENV', 'development').lower()
    
    if env == 'production':
        return ProductionConfig
    elif env == 'testing':
        return TestingConfig
    else:
        return DevelopmentConfig
