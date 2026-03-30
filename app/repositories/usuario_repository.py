"""
Repositorio para Usuario.
Capa de acceso a datos.
"""

from app.models import Usuario


class UsuarioRepository:
    """Repositorio para operaciones de Usuario."""
    
    def __init__(self, db):
        self.db = db
    
    def obtener_por_id(self, id_usuario):
        """Obtener usuario por ID."""
        return Usuario.query.get(id_usuario)
    
    def obtener_por_email(self, email):
        """Obtener usuario por email."""
        return Usuario.query.filter_by(email=email).first()
    
    def obtener_todos(self):
        """Obtener todos los usuarios."""
        return Usuario.query.all()
    
    def obtener_activos(self):
        """Obtener solo usuarios activos."""
        return Usuario.query.filter_by(activo=True).all()
    
    def crear(self, nombre, email, password_hash, rol='ADMIN'):
        """Crear un nuevo usuario."""
        usuario = Usuario(
            nombre=nombre,
            email=email,
            password_hash=password_hash,
            rol=rol,
            activo=True
        )
        self.db.session.add(usuario)
        self.db.session.commit()
        return usuario
    
    def actualizar(self, id_usuario, **kwargs):
        """Actualizar un usuario."""
        usuario = self.obtener_por_id(id_usuario)
        if usuario:
            for key, value in kwargs.items():
                if hasattr(usuario, key):
                    setattr(usuario, key, value)
            self.db.session.commit()
        return usuario
    
    def eliminar(self, id_usuario):
        """Eliminar un usuario."""
        usuario = self.obtener_por_id(id_usuario)
        if usuario:
            self.db.session.delete(usuario)
            self.db.session.commit()
            return True
        return False
    
    def registrar_ultimo_login(self, id_usuario):
        """Registrar el último login."""
        from datetime import datetime
        usuario = self.obtener_por_id(id_usuario)
        if usuario:
            usuario.ultimo_login = datetime.utcnow()
            self.db.session.commit()
