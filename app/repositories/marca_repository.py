"""
Repositorio para Marca.
Capa de acceso a datos.
"""

from app.models import Marca


class MarcaRepository:
    """Repositorio para operaciones de Marca."""
    
    def __init__(self, db):
        self.db = db
    
    def obtener_por_id(self, id_marca):
        """Obtener marca por ID."""
        return Marca.query.get(id_marca)
    
    def obtener_todas(self):
        """Obtener todas las marcas."""
        return Marca.query.order_by(Marca.nombre).all()
    
    def obtener_activas(self):
        """Obtener solo marcas activas."""
        return Marca.query.filter_by(activo=True).order_by(Marca.nombre).all()
    
    def obtener_por_nombre(self, nombre):
        """Obtener marca por nombre."""
        return Marca.query.filter_by(nombre=nombre).first()
    
    def crear(self, nombre, descripcion=None, activo=True):
        """Crear una nueva marca."""
        marca = Marca(
            nombre=nombre,
            descripcion=descripcion,
            activo=activo
        )
        self.db.session.add(marca)
        self.db.session.commit()
        return marca
    
    def actualizar(self, id_marca, **kwargs):
        """Actualizar una marca."""
        marca = self.obtener_por_id(id_marca)
        if marca:
            for key, value in kwargs.items():
                if hasattr(marca, key):
                    setattr(marca, key, value)
            self.db.session.commit()
        return marca
    
    def eliminar(self, id_marca):
        """Eliminar una marca (si no tiene productos)."""
        marca = self.obtener_por_id(id_marca)
        if marca:
            # Verificar que no tenga productos
            if marca.productos.count() == 0:
                self.db.session.delete(marca)
                self.db.session.commit()
                return True
        return False
    
    def contar(self):
        """Contar marcas totales."""
        return Marca.query.count()
