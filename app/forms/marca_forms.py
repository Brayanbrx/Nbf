"""
Formularios WTForms para marcas.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from app.models import Marca


class FormularioMarca(FlaskForm):
    """Formulario para crear/editar marcas."""
    
    nombre = StringField(
        'Nombre',
        validators=[
            DataRequired(message='El nombre es requerido.'),
            Length(min=3, max=100, message='El nombre debe tener entre 3 y 100 caracteres.')
        ],
        render_kw={'class': 'form-control', 'placeholder': 'Ej: Sony, LG, Samsung'}
    )
    
    descripcion = TextAreaField(
        'Descripción',
        validators=[Length(max=255, message='Máximo 255 caracteres.')],
        render_kw={'class': 'form-control', 'placeholder': 'Descripción opcional', 'rows': 3}
    )
    
    activo = BooleanField(
        'Activo',
        render_kw={'class': 'form-check-input'}
    )
    
    submit = SubmitField(
        'Guardar Marca',
        render_kw={'class': 'btn btn-primary'}
    )
    
    def validate_nombre(self, field):
        """Validar que el nombre sea único."""
        marca_existente = Marca.query.filter_by(nombre=field.data).first()
        if marca_existente:
            if not hasattr(self, 'id_marca_edit') or self.id_marca_edit != marca_existente.id_marca:
                raise ValidationError('Ya existe una marca con ese nombre.')
