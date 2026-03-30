"""
Blueprint público - Catálogo público sin login.
Rutas: /, /catalogo, /catalogo/producto/<id>
"""

from flask import Blueprint, render_template, request, abort
from app.services import ProductoService, CategoriaService, MarcaService

public_bp = Blueprint('public', __name__)

# Instanciar servicios
producto_service = ProductoService()
categoria_service = CategoriaService()
marca_service = MarcaService()


@public_bp.route('/')
def home():
    """Página de inicio."""
    productos_destacados = producto_service.obtener_publicos()[:6]
    return render_template(
        'public/home.html',
        productos_destacados=productos_destacados,
        total_productos=producto_service.contar_publicos()
    )


@public_bp.route('/catalogo')
def catalogo():
    """Página de catálogo con búsqueda y filtros."""
    pagina = request.args.get('pagina', 1, type=int)
    busqueda = request.args.get('busqueda', '', type=str)
    id_categoria = request.args.get('categoria', None, type=int)
    id_marca = request.args.get('marca', None, type=int)
    
    # Construir filtros
    filtros = {}
    if busqueda:
        filtros['busqueda'] = busqueda
    if id_categoria:
        filtros['id_categoria'] = id_categoria
    if id_marca:
        filtros['id_marca'] = id_marca
    
    # Buscar con paginación
    paginacion = producto_service.buscar_publicos(
        filtros=filtros,
        pagina=pagina,
        por_pagina=12
    )
    
    return render_template(
        'public/catalogo.html',
        productos=paginacion.items,
        paginacion=paginacion,
        busqueda=busqueda,
        id_categoria=id_categoria,
        id_marca=id_marca,
        categorias=categoria_service.obtener_activas(),
        marcas=marca_service.obtener_activas()
    )


@public_bp.route('/catalogo/producto/<int:id_producto>')
def detalle_producto(id_producto):
    """Detalle de un producto."""
    producto = producto_service.obtener_por_id(id_producto)
    
    if not producto or not producto.es_visible_publico():
        abort(404)
    
    # Productos relacionados (misma categoría)
    relacionados = producto_service.obtener_productos_por_categoria(
        producto.id_categoria,
        solo_publicos=True
    )[:4]
    
    return render_template(
        'public/producto_detalle.html',
        producto=producto,
        relacionados=relacionados
    )
