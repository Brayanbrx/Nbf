"""
Paquete forms - exportar todos los formularios.
"""

from app.forms.auth_forms import FormularioLogin
from app.forms.categoria_forms import FormularioCategoria
from app.forms.marca_forms import FormularioMarca
from app.forms.producto_forms import FormularioProducto

__all__ = [
    'FormularioLogin',
    'FormularioCategoria',
    'FormularioMarca',
    'FormularioProducto',
]
