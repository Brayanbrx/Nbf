"""
Formularios WTForms para productos.
"""

from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DecimalField, IntegerField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, NumberRange, ValidationError, Optional
from app.models import Producto


class FormularioProducto(FlaskForm):
    """Formulario para crear/editar productos."""
    
    codigo = StringField(
        'Código',
        validators=[
            DataRequired(message='El código es requerido.'),
            Length(min=2, max=50, message='El código debe tener entre 2 y 50 caracteres.')
        ],
        render_kw={'class': 'form-control', 'placeholder': 'Ej: PROD-001'}
    )
    
    nombre = StringField(
        'Nombre',
        validators=[
            DataRequired(message='El nombre es requerido.'),
            Length(min=3, max=150, message='El nombre debe tener entre 3 y 150 caracteres.')
        ],
        render_kw={'class': 'form-control', 'placeholder': 'Nombre del producto'}
    )
    
    descripcion = TextAreaField(
        'Descripción',
        validators=[Length(max=255, message='Máximo 255 caracteres.')],
        render_kw={'class': 'form-control', 'placeholder': 'Descripción (opcional)', 'rows': 3}
    )
    
    url_imagen = StringField(
        'URL de la Imagen',
        validators=[Length(max=500, message='URL muy larga.')],
        render_kw={'class': 'form-control', 'placeholder': 'https://ejemplo.com/imagen.jpg'}
    )
    
    id_categoria = SelectField(
        'Categoría',
        coerce=int,
        validators=[DataRequired(message='Selecciona una categoría.')],
        render_kw={'class': 'form-select'}
    )
    
    id_marca = SelectField(
        'Marca',
        coerce=int,
        validators=[DataRequired(message='Selecciona una marca.')],
        render_kw={'class': 'form-select'}
    )
    
    # Precios
    precio_paquete_bs = DecimalField(
        'Precio Paquete (Bs)',
        validators=[Optional(), NumberRange(min=0, message='El precio no puede ser negativo.')],
        places=2,
        render_kw={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}
    )
    
    precio_docena_bs = DecimalField(
        'Precio Docena (Bs)',
        validators=[Optional(), NumberRange(min=0, message='El precio no puede ser negativo.')],
        places=2,
        render_kw={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}
    )
    
    precio_caja_bs = DecimalField(
        'Precio Caja (Bs)',
        validators=[Optional(), NumberRange(min=0, message='El precio no puede ser negativo.')],
        places=2,
        render_kw={'class': 'form-control', 'placeholder': '0.00', 'step': '0.01'}
    )
    
    # Unidades
    unidades_por_paquete = IntegerField(
        'Unidades por Paquete',
        validators=[Optional(), NumberRange(min=1, message='Debe ser mayor a 0.')],
        render_kw={'class': 'form-control', 'placeholder': 'Ej: 6'}
    )
    
    unidades_por_docena = IntegerField(
        'Unidades por Docena',
        validators=[NumberRange(min=1, message='Debe ser mayor a 0.')],
        render_kw={'class': 'form-control', 'value': '12'}
    )
    
    unidades_por_caja = IntegerField(
        'Unidades por Caja',
        validators=[NumberRange(min=1, message='Debe ser mayor a 0.')],
        render_kw={'class': 'form-control', 'placeholder': 'Ej: 48'}
    )
    
    # Estado
    activo = BooleanField(
        'Activo',
        render_kw={'class': 'form-check-input'}
    )
    
    visible_catalogo_publico = BooleanField(
        'Visible en Catálogo Público',
        render_kw={'class': 'form-check-input'}
    )
    
    # Mostrar precios
    mostrar_precio_paquete = BooleanField(
        'Mostrar Precio Paquete',
        render_kw={'class': 'form-check-input'}
    )
    
    mostrar_precio_docena = BooleanField(
        'Mostrar Precio Docena',
        render_kw={'class': 'form-check-input'}
    )
    
    mostrar_precio_caja = BooleanField(
        'Mostrar Precio Caja',
        render_kw={'class': 'form-check-input'}
    )
    
    submit = SubmitField(
        'Guardar Producto',
        render_kw={'class': 'btn btn-primary'}
    )
    
    def validate_codigo(self, field):
        """Validar que el código sea único (excepto en edición)."""
        producto_existente = Producto.query.filter_by(codigo=field.data).first()
        if producto_existente:
            # Si estamos editando y el código es del mismo producto, permitir
            if self.id_producto_edit is None or self.id_producto_edit != producto_existente.id_producto:
                raise ValidationError('Ya existe un producto con ese código.')
    
    def __init__(self, id_producto_edit=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.id_producto_edit = id_producto_edit
        # Cargar opciones de categorías y marcas dinámicamente
        from app.models import Categoria, Marca
        self.id_categoria.choices = [
            (c.id_categoria, c.nombre) for c in Categoria.query.filter_by(activo=True).all()
        ]
        self.id_marca.choices = [
            (m.id_marca, m.nombre) for m in Marca.query.filter_by(activo=True).all()
        ]
