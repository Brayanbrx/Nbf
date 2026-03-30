"""
Decoradores personalizados.
Para control de acceso y autorización.
"""

from functools import wraps
from flask import redirect, url_for, flash, abort
from flask_login import current_user


def admin_required(f):
    """Decorador que requiere que el usuario sea admin."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Debes iniciar sesión.', 'warning')
            return redirect(url_for('auth.login'))
        
        if not current_user.es_admin():
            flash('No tienes permisos de administrador.', 'danger')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function


def editor_required(f):
    """Decorador que requiere editor o admin."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            flash('Debes iniciar sesión.', 'warning')
            return redirect(url_for('auth.login'))
        
        if not (current_user.es_admin() or current_user.es_editor()):
            flash('No tienes permisos suficientes.', 'danger')
            abort(403)
        
        return f(*args, **kwargs)
    return decorated_function
