"""
Servicio para Categoría.
Lógica de negocio.
"""

from app.repositories.categoria_repository import CategoriaRepository
from app.extensions import db, cache


class CategoriaService:
    """Servicio de categorías."""
    
    def __init__(self):
        self.repo = CategoriaRepository(db)
    
    def obtener_todas(self):
        """Obtener todas las categorías (cached)."""
        return cache.get('categorias_todas') or self._actualizar_cache_categorias()
    
    def obtener_activas(self):
        """Obtener categorías activas (cached)."""
        return cache.get('categorias_activas') or self._actualizar_cache_activas()
    
    def _actualizar_cache_categorias(self):
        """Actualizar cache de todas las categorías."""
        resultado = self.repo.obtener_todas()
        cache.set('categorias_todas', resultado, timeout=3600)  # 1 hora
        return resultado
    
    def _actualizar_cache_activas(self):
        """Actualizar cache de categorías activas."""
        resultado = self.repo.obtener_activas()
        cache.set('categorias_activas', resultado, timeout=3600)  # 1 hora
        return resultado
    
    def obtener_por_id(self, id_categoria):
        """Obtener categoría específica."""
        return self.repo.obtener_por_id(id_categoria)
    
    def crear(self, nombre, descripcion=None):
        """
        Crear nueva categoría.
        
        Raises:
            ValueError si el nombre ya existe.
        """
        if self.repo.obtener_por_nombre(nombre):
            raise ValueError(f"La categoría '{nombre}' ya existe.")
        
        resultado = self.repo.crear(nombre, descripcion, activo=True)
        # Invalidar caches
        cache.delete('categorias_todas')
        cache.delete('categorias_activas')
        return resultado
    
    def actualizar(self, id_categoria, nombre, descripcion=None, activo=None):
        """Actualizar categoría."""
        # Verificar que el nombre sea único (si cambió)
        existente = self.repo.obtener_por_nombre(nombre)
        if existente and existente.id_categoria != id_categoria:
            raise ValueError(f"Ya existe una categoría con ese nombre.")
        
        datos = {'nombre': nombre, 'descripcion': descripcion}
        if activo is not None:
            datos['activo'] = activo
        
        resultado = self.repo.actualizar(id_categoria, **datos)
        # Invalidar caches
        cache.delete('categorias_todas')
        cache.delete('categorias_activas')
        return resultado
    
    def eliminar(self, id_categoria):
        """
        Eliminar categoría.
        
        Returns:
            True si se eliminó, False si no (ej: tiene productos).
        """
        resultado = self.repo.eliminar(id_categoria)
        if resultado:
            # Invalidar caches si fue exitoso
            cache.delete('categorias_todas')
            cache.delete('categorias_activas')
        return resultado
    
    def contar(self):
        """Contar categorías."""
        return self.repo.contar()
