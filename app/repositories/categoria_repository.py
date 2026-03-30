"""
Repositorio para Categoria.
Capa de acceso a datos.
"""

from app.models import Categoria


class CategoriaRepository:
    """Repositorio para operaciones de Categoria."""
    
    def __init__(self, db):
        self.db = db
    
    def obtener_por_id(self, id_categoria):
        """Obtener categoría por ID."""
        return Categoria.query.get(id_categoria)
    
    def obtener_todas(self):
        """Obtener todas las categorías."""
        return Categoria.query.order_by(Categoria.nombre).all()
    
    def obtener_activas(self):
        """Obtener solo categorías activas."""
        return Categoria.query.filter_by(activo=True).order_by(Categoria.nombre).all()
    
    def obtener_por_nombre(self, nombre):
        """Obtener categoría por nombre."""
        return Categoria.query.filter_by(nombre=nombre).first()
    
    def crear(self, nombre, descripcion=None, activo=True):
        """Crear una nueva categoría."""
        categoria = Categoria(
            nombre=nombre,
            descripcion=descripcion,
            activo=activo
        )
        self.db.session.add(categoria)
        self.db.session.commit()
        return categoria
    
    def actualizar(self, id_categoria, **kwargs):
        """Actualizar una categoría."""
        categoria = self.obtener_por_id(id_categoria)
        if categoria:
            for key, value in kwargs.items():
                if hasattr(categoria, key):
                    setattr(categoria, key, value)
            self.db.session.commit()
        return categoria
    
    def eliminar(self, id_categoria):
        """Eliminar una categoría (si no tiene productos)."""
        categoria = self.obtener_por_id(id_categoria)
        if categoria:
            # Verificar que no tenga productos
            if categoria.productos.count() == 0:
                self.db.session.delete(categoria)
                self.db.session.commit()
                return True
        return False
    
    def contar(self):
        """Contar categorías totales."""
        return Categoria.query.count()
