"""
Paquete repositories - exportar todos los repositorios.
"""

from app.repositories.usuario_repository import UsuarioRepository
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.marca_repository import MarcaRepository
from app.repositories.producto_repository import ProductoRepository

__all__ = [
    'UsuarioRepository',
    'CategoriaRepository',
    'MarcaRepository',
    'ProductoRepository',
]
