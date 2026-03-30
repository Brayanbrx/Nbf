"""
Servicio para Producto.
Lógica de negocio compleja.
"""

from app.repositories.producto_repository import ProductoRepository
from app.extensions import db, cache


class ProductoService:
    """Servicio de productos."""
    
    def __init__(self):
        self.repo = ProductoRepository(db)
    
    def obtener_publicos(self):
        """Obtener productos públicos (cached)."""
        return cache.get('productos_publicos') or self._actualizar_cache_publicos()
    
    def _actualizar_cache_publicos(self):
        """Actualizar cache de productos públicos."""
        resultado = self.repo.obtener_publicos()
        cache.set('productos_publicos', resultado, timeout=1800)  # 30 minutos
        return resultado
    
    def obtener_por_id(self, id_producto):
        """Obtener producto específico."""
        return self.repo.obtener_por_id(id_producto)
    
    def obtener_por_codigo(self, codigo):
        """Obtener producto por código."""
        return self.repo.obtener_por_codigo(codigo)
    
    def buscar_publicos(self, filtros=None, pagina=1, por_pagina=12):
        """Buscar productos públicos con paginación."""
        return self.repo.buscar_publicos(filtros, pagina, por_pagina)
    
    def buscar_admin(self, filtros=None, pagina=1, por_pagina=20):
        """Buscar productos para panel admin."""
        return self.repo.buscar_admin(filtros, pagina, por_pagina)
    
    def crear(self, codigo, nombre, id_categoria, id_marca,
              precio_paquete_bs=0, precio_docena_bs=0, precio_caja_bs=0,
              unidades_por_paquete=None, unidades_por_docena=12, unidades_por_caja=1,
              descripcion=None, url_imagen=None, activo=True,
              visible_catalogo_publico=True, mostrar_precio_paquete=False,
              mostrar_precio_docena=False, mostrar_precio_caja=False):
        """
        Crear nuevo producto.
        
        Raises:
            ValueError si código ya existe.
        """
        if self.repo.obtener_por_codigo(codigo):
            raise ValueError(f"Ya existe un producto con código '{codigo}'.")
        
        # Validaciones de negocio
        if unidades_por_caja <= 0:
            raise ValueError("Unidades por caja debe ser mayor a 0.")
        
        if unidades_por_docena <= 0:
            raise ValueError("Unidades por docena debe ser mayor a 0.")
        
        if unidades_por_paquete is not None and unidades_por_paquete <= 0:
            raise ValueError("Unidades por paquete debe ser mayor a 0.")
        
        resultado = self.repo.crear(
            codigo=codigo,
            nombre=nombre,
            id_categoria=id_categoria,
            id_marca=id_marca,
            precio_paquete_bs=precio_paquete_bs or 0,
            precio_docena_bs=precio_docena_bs or 0,
            precio_caja_bs=precio_caja_bs or 0,
            unidades_por_paquete=unidades_por_paquete,
            unidades_por_docena=unidades_por_docena,
            unidades_por_caja=unidades_por_caja,
            descripcion=descripcion,
            url_imagen=url_imagen,
            activo=activo,
            visible_catalogo_publico=visible_catalogo_publico,
            mostrar_precio_paquete=mostrar_precio_paquete,
            mostrar_precio_docena=mostrar_precio_docena,
            mostrar_precio_caja=mostrar_precio_caja
        )
        
        # Invalidar caches
        self._invalidar_caches()
        return resultado
    
    def actualizar(self, id_producto, **kwargs):
        """Actualizar producto."""
        producto = self.obtener_por_id(id_producto)
        if not producto:
            raise ValueError("Producto no encontrado.")
        
        # Si cambia el código, verificar que sea único
        if 'codigo' in kwargs:
            existente = self.repo.obtener_por_codigo(kwargs['codigo'])
            if existente and existente.id_producto != id_producto:
                raise ValueError(f"Ya existe un producto con código '{kwargs['codigo']}'.")
        
        resultado = self.repo.actualizar(id_producto, **kwargs)
        
        # Invalidar caches
        self._invalidar_caches()
        return resultado
    
    def eliminar(self, id_producto):
        """Eliminar producto."""
        resultado = self.repo.eliminar(id_producto)
        if resultado:
            # Invalidar caches si fue exitoso
            self._invalidar_caches()
        return resultado
    
    def _invalidar_caches(self):
        """Invalidar todos los caches relacionados con productos."""
        cache.delete('productos_publicos')
    
    def cambiar_estado_activo(self, id_producto, activo):
        """Cambiar estado activo/inactivo."""
        return self.actualizar(id_producto, activo=activo)
    
    def cambiar_visibilidad_publica(self, id_producto, visible):
        """Cambiar visibilidad en catálogo público."""
        return self.actualizar(id_producto, visible_catalogo_publico=visible)
    
    def contar(self):
        """Contar total de productos."""
        return self.repo.contar()
    
    def contar_publicos(self):
        """Contar productos públicos."""
        return self.repo.contar_publicos()
    
    def obtener_productos_por_categoria(self, id_categoria, solo_publicos=True):
        """Obtener productos de una categoría."""
        return self.repo.obtener_productos_por_categoria(id_categoria, solo_publicos)
    
    def obtener_productos_por_marca(self, id_marca, solo_publicos=True):
        """Obtener productos de una marca."""
        return self.repo.obtener_productos_por_marca(id_marca, solo_publicos)
