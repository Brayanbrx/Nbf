"""
Fábrica de aplicación Flask.
Inicializa y configura toda la aplicación.
"""

from flask import Flask
from flask_login import LoginManager

from app.config import get_config
from app.extensions import db, migrate, login_manager, csrf, cache, compress


def create_app(environment='development'):
    """
    Crear y configurar la aplicación Flask.
    
    Args:
        environment: 'development', 'production' o 'testing'
    
    Returns:
        Aplicación Flask configurada
    """
    
    # Crear instancia de Flask
    app = Flask(__name__)
    
    # Cargar configuración
    config_class = get_config()
    app.config.from_object(config_class)
    
    # Inicializar extensiones
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    csrf.init_app(app)
    cache.init_app(app)
    compress.init_app(app)
    
    # Contexto de shell de Flask
    @app.shell_context_processor
    def make_shell_context():
        from app.models import Usuario, Categoria, Marca, Producto
        return {
            'db': db,
            'Usuario': Usuario,
            'Categoria': Categoria,
            'Marca': Marca,
            'Producto': Producto,
        }
    
    # Crear tablas si no existen (solo desarrollo)
    with app.app_context():
        db.create_all()
    
    # Registrar blueprints (módulos de rutas)
    register_blueprints(app)
    
    # Configurar login manager
    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Por favor inicia sesión para acceder.'
    
    @login_manager.user_loader
    def load_user(user_id):
        from app.models import Usuario
        return Usuario.query.get(int(user_id))
    
    # Procesadores de contexto para templates
    @app.context_processor
    def context_processor():
        """Variables globales para los templates."""
        from app.services import CategoriaService, MarcaService
        from datetime import datetime
        
        categoria_service = CategoriaService()
        marca_service = MarcaService()
        
        return {
            'categorias': categoria_service.obtener_activas(),
            'marcas': marca_service.obtener_activas(),
            'now': datetime.utcnow(),
        }
    
    return app


def register_blueprints(app):
    """Registrar todos los blueprints."""
    
    # Blueprint Público (catálogo)
    from app.blueprints.public import public_bp
    app.register_blueprint(public_bp)
    
    # Blueprint Autenticación
    from app.blueprints.auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    # Blueprint Admin
    from app.blueprints.admin import admin_bp
    app.register_blueprint(admin_bp, url_prefix='/admin')
