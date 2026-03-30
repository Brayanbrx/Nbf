"""
Formularios WTForms para categorías.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from app.models import Categoria


class FormularioCategoria(FlaskForm):
    """Formulario para crear/editar categorías."""
    
    nombre = StringField(
        'Nombre',
        validators=[
            DataRequired(message='El nombre es requerido.'),
            Length(min=3, max=100, message='El nombre debe tener entre 3 y 100 caracteres.')
        ],
        render_kw={'class': 'form-control', 'placeholder': 'Ej: Electrónica'}
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
        'Guardar Categoría',
        render_kw={'class': 'btn btn-primary'}
    )
    
    def validate_nombre(self, field):
        """Validar que el nombre sea único (excepto si estamos editando el mismo)."""
        # En edición, se pasará el id_categoria para excluirlo
        categoria_existente = Categoria.query.filter_by(nombre=field.data).first()
        if categoria_existente:
            # Si estamos creando (sin id) o editando (con id distinto)
            if not hasattr(self, 'id_categoria_edit') or self.id_categoria_edit != categoria_existente.id_categoria:
                raise ValidationError('Ya existe una categoría con ese nombre.')
