"""
Servicio para Marca.
Lógica de negocio.
"""

from app.repositories.marca_repository import MarcaRepository
from app.extensions import db, cache


class MarcaService:
    """Servicio de marcas."""
    
    def __init__(self):
        self.repo = MarcaRepository(db)
    
    def obtener_todas(self):
        """Obtener todas las marcas (cached)."""
        return cache.get('marcas_todas') or self._actualizar_cache_marcas()
    
    def obtener_activas(self):
        """Obtener marcas activas (cached)."""
        return cache.get('marcas_activas') or self._actualizar_cache_activas()
    
    def _actualizar_cache_marcas(self):
        """Actualizar cache de todas las marcas."""
        resultado = self.repo.obtener_todas()
        cache.set('marcas_todas', resultado, timeout=3600)  # 1 hora
        return resultado
    
    def _actualizar_cache_activas(self):
        """Actualizar cache de marcas activas."""
        resultado = self.repo.obtener_activas()
        cache.set('marcas_activas', resultado, timeout=3600)  # 1 hora
        return resultado
    
    def obtener_por_id(self, id_marca):
        """Obtener marca específica."""
        return self.repo.obtener_por_id(id_marca)
    
    def crear(self, nombre, descripcion=None):
        """
        Crear nueva marca.
        
        Raises:
            ValueError si el nombre ya existe.
        """
        if self.repo.obtener_por_nombre(nombre):
            raise ValueError(f"La marca '{nombre}' ya existe.")
        
        resultado = self.repo.crear(nombre, descripcion, activo=True)
        # Invalidar caches
        cache.delete('marcas_todas')
        cache.delete('marcas_activas')
        return resultado
    
    def actualizar(self, id_marca, nombre, descripcion=None, activo=None):
        """Actualizar marca."""
        # Verificar que el nombre sea único (si cambió)
        existente = self.repo.obtener_por_nombre(nombre)
        if existente and existente.id_marca != id_marca:
            raise ValueError(f"Ya existe una marca con ese nombre.")
        
        datos = {'nombre': nombre, 'descripcion': descripcion}
        if activo is not None:
            datos['activo'] = activo
        
        resultado = self.repo.actualizar(id_marca, **datos)
        # Invalidar caches
        cache.delete('marcas_todas')
        cache.delete('marcas_activas')
        return resultado
    
    def eliminar(self, id_marca):
        """
        Eliminar marca.
        
        Returns:
            True si se eliminó, False si no (ej: tiene productos).
        """
        resultado = self.repo.eliminar(id_marca)
        if resultado:
            # Invalidar caches si fue exitoso
            cache.delete('marcas_todas')
            cache.delete('marcas_activas')
        return resultado
    
    def contar(self):
        """Contar marcas."""
        return self.repo.contar()
