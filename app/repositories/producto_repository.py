"""
Repositorio para Producto.
Capa de acceso a datos con búsqueda y filtros.
"""

from app.models import Producto
from sqlalchemy import and_


class ProductoRepository:
    """Repositorio para operaciones de Producto."""
    
    def __init__(self, db):
        self.db = db
    
    def obtener_por_id(self, id_producto):
        """Obtener producto por ID."""
        return Producto.query.get(id_producto)
    
    def obtener_por_codigo(self, codigo):
        """Obtener producto por código."""
        return Producto.query.filter_by(codigo=codigo).first()
    
    def obtener_todos(self):
        """Obtener todos los productos."""
        return Producto.query.order_by(Producto.nombre).all()
    
    def obtener_activos(self):
        """Obtener solo productos activos."""
        return Producto.query.filter_by(activo=True).order_by(Producto.nombre).all()
    
    def obtener_publicos(self):
        """Obtener productos visibles en catálogo público."""
        return Producto.query.filter(
            and_(
                Producto.activo == True,
                Producto.visible_catalogo_publico == True
            )
        ).order_by(Producto.nombre).all()
    
    def buscar_publicos(self, filtros=None, pagina=1, por_pagina=12):
        """
        Buscar productos públicos con filtros.
        
        Args:
            filtros (dict): {
                'busqueda': str (código o nombre),
                'id_categoria': int,
                'id_marca': int
            }
            pagina: número de página (1-indexed)
            por_pagina: productos por página
        
        Returns:
            Paginator de Flask-SQLAlchemy
        """
        query = Producto.query.filter(
            and_(
                Producto.activo == True,
                Producto.visible_catalogo_publico == True
            )
        )
        
        if filtros:
            # Búsqueda por código o nombre
            if filtros.get('busqueda'):
                busqueda = f"%{filtros['busqueda']}%"
                from sqlalchemy import or_
                query = query.filter(
                    or_(
                        Producto.codigo.ilike(busqueda),
                        Producto.nombre.ilike(busqueda)
                    )
                )
            
            # Filtro por categoría
            if filtros.get('id_categoria'):
                query = query.filter_by(id_categoria=filtros['id_categoria'])
            
            # Filtro por marca
            if filtros.get('id_marca'):
                query = query.filter_by(id_marca=filtros['id_marca'])
        
        return query.order_by(Producto.nombre).paginate(
            page=pagina,
            per_page=por_pagina,
            error_out=False
        )
    
    def buscar_admin(self, filtros=None, pagina=1, por_pagina=20):
        """
        Buscar productos para panel admin con filtros.
        
        Args:
            filtros (dict): {
                'busqueda': str,
                'id_categoria': int,
                'id_marca': int,
                'activo': bool (True/False/None para todos)
            }
            pagina: número de página
            por_pagina: productos por página
        
        Returns:
            Paginator de Flask-SQLAlchemy
        """
        query = Producto.query
        
        if filtros:
            # Búsqueda
            if filtros.get('busqueda'):
                busqueda = f"%{filtros['busqueda']}%"
                from sqlalchemy import or_
                query = query.filter(
                    or_(
                        Producto.codigo.ilike(busqueda),
                        Producto.nombre.ilike(busqueda)
                    )
                )
            
            # Categoría
            if filtros.get('id_categoria'):
                query = query.filter_by(id_categoria=filtros['id_categoria'])
            
            # Marca
            if filtros.get('id_marca'):
                query = query.filter_by(id_marca=filtros['id_marca'])
            
            # Activo/Inactivo
            if filtros.get('activo') is not None:
                query = query.filter_by(activo=filtros['activo'])
        
        return query.order_by(Producto.nombre.desc()).paginate(
            page=pagina,
            per_page=por_pagina,
            error_out=False
        )
    
    def crear(self, **kwargs):
        """Crear un nuevo producto."""
        producto = Producto(**kwargs)
        self.db.session.add(producto)
        self.db.session.commit()
        return producto
    
    def actualizar(self, id_producto, **kwargs):
        """Actualizar un producto."""
        from datetime import datetime
        producto = self.obtener_por_id(id_producto)
        if producto:
            for key, value in kwargs.items():
                if hasattr(producto, key):
                    setattr(producto, key, value)
            # Actualizar fecha de actualización
            producto.fecha_actualizacion = datetime.utcnow()
            self.db.session.commit()
        return producto
    
    def eliminar(self, id_producto):
        """Eliminar un producto."""
        producto = self.obtener_por_id(id_producto)
        if producto:
            self.db.session.delete(producto)
            self.db.session.commit()
            return True
        return False
    
    def contar(self):
        """Contar total de productos."""
        return Producto.query.count()
    
    def contar_publicos(self):
        """Contar productos públicos."""
        return Producto.query.filter(
            and_(
                Producto.activo == True,
                Producto.visible_catalogo_publico == True
            )
        ).count()
    
    def obtener_productos_por_categoria(self, id_categoria, solo_publicos=True):
        """Obtener productos de una categoría."""
        query = Producto.query.filter_by(id_categoria=id_categoria)
        if solo_publicos:
            query = query.filter(
                and_(
                    Producto.activo == True,
                    Producto.visible_catalogo_publico == True
                )
            )
        return query.all()
    
    def obtener_productos_por_marca(self, id_marca, solo_publicos=True):
        """Obtener productos de una marca."""
        query = Producto.query.filter_by(id_marca=id_marca)
        if solo_publicos:
            query = query.filter(
                and_(
                    Producto.activo == True,
                    Producto.visible_catalogo_publico == True
                )
            )
        return query.all()
