"""
Formularios WTForms para autenticación.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length, ValidationError
from app.repositories.usuario_repository import UsuarioRepository
from app.extensions import db


class FormularioLogin(FlaskForm):
    """Formulario de inicio de sesión."""
    
    email = StringField(
        'Email',
        validators=[
            DataRequired(message='El email es requerido.'),
            Email(message='Email inválido.')
        ],
        render_kw={'class': 'form-control', 'placeholder': 'tu@email.com'}
    )
    
    password = PasswordField(
        'Contraseña',
        validators=[
            DataRequired(message='La contraseña es requerida.'),
            Length(min=6, message='La contraseña debe tener al menos 6 caracteres.')
        ],
        render_kw={'class': 'form-control', 'placeholder': 'Tu contraseña'}
    )
    
    submit = SubmitField(
        'Iniciar Sesión',
        render_kw={'class': 'btn btn-primary w-100'}
    )
