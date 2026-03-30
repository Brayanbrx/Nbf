"""
Blueprint de autenticación.
Rutas: /auth/login, /auth/logout
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user

from app.forms import FormularioLogin
from app.services import AuthService

auth_bp = Blueprint('auth', __name__)
auth_service = AuthService()


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de login."""
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    
    formulario = FormularioLogin()
    
    if formulario.validate_on_submit():
        email = formulario.email.data
        password = formulario.password.data
        
        # Intentar autenticar
        usuario = auth_service.autenticar(email, password)
        
        if usuario:
            login_user(usuario, remember=True)
            flash(f'¡Bienvenido, {usuario.nombre}!', 'success')
            
            # Redirigir a admin o a dónde vino
            siguiente = request.args.get('next')
            if siguiente and siguiente.startswith('/admin'):
                return redirect(siguiente)
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Email o contraseña incorrectos.', 'danger')
    
    return render_template('auth/login.html', form=formulario)


@auth_bp.route('/logout')
def logout():
    """Cerrar sesión."""
    logout_user()
    flash('Sesión cerrada correctamente.', 'info')
    return redirect(url_for('public.home'))
