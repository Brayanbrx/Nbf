"""
Funciones de seguridad.
"""

from werkzeug.security import generate_password_hash, check_password_hash


def hash_password(password):
    """Hashear contraseña."""
    return generate_password_hash(password)


def verify_password(hashed, password):
    """Verificar contraseña contra hash."""
    return check_password_hash(hashed, password)
