"""
Servicio de autenticación.
Lógica de negocio para login/logout.
"""

from werkzeug.security import generate_password_hash
from app.repositories.usuario_repository import UsuarioRepository
from app.extensions import db


class AuthService:
    """Servicio de autenticación."""
    
    def __init__(self):
        self.repo = UsuarioRepository(db)
    
    def autenticar(self, email, password):
        """
        Autenticar usuario.
        
        Returns:
            Usuario si credenciales son correctas, None si es inválido.
        """
        usuario = self.repo.obtener_por_email(email)
        if usuario and usuario.activo and usuario.check_password(password):
            self.repo.registrar_ultimo_login(usuario.id_usuario)
            return usuario
        return None
    
    def crear_usuario(self, nombre, email, password, rol='ADMIN'):
        """
        Crear nuevo usuario con password hasheado.
        
        Returns:
            Usuario creado o None si hay error (ej: email duplicado).
        """
        # Verificar que el email no exista
        if self.repo.obtener_por_email(email):
            raise ValueError(f"El email {email} ya está registrado.")
        
        # Hashear password
        password_hash = generate_password_hash(password)
        
        # Crear usuario
        return self.repo.crear(
            nombre=nombre,
            email=email,
            password_hash=password_hash,
            rol=rol
        )
    
    def cambiar_password(self, id_usuario, password_actual, password_nuevo):
        """Cambiar contraseña de un usuario."""
        usuario = self.repo.obtener_por_id(id_usuario)
        if not usuario:
            return False
        
        # Verificar password actual
        if not usuario.check_password(password_actual):
            return False
        
        # Actualizar
        usuario.password_hash = generate_password_hash(password_nuevo)
        db.session.commit()
        return True
