"""
Blueprint de administración.
Panel admin para CRUD de productos, categorías y marcas.
Rutas: /admin/*
"""

from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user

from app.forms import (
    FormularioProducto,
    FormularioCategoria,
    FormularioMarca
)
from app.services import (
    ProductoService,
    CategoriaService,
    MarcaService
)
from app.utils import admin_required

admin_bp = Blueprint('admin', __name__)

# Instanciar servicios
producto_service = ProductoService()
categoria_service = CategoriaService()
marca_service = MarcaService()


# =====================
# DASHBOARD
# =====================

@admin_bp.route('/')
@admin_required
def dashboard():
    """Dashboard principal del admin."""
    stats = {
        'total_productos': producto_service.contar(),
        'categorias': categoria_service.contar(),
        'marcas': marca_service.contar(),
    }
    return render_template('admin/dashboard.html', stats=stats)


# =====================
# PRODUCTOS
# =====================

@admin_bp.route('/productos')
@admin_required
def productos_listado():
    """Listado de productos con filtros."""
    pagina = request.args.get('pagina', 1, type=int)
    busqueda = request.args.get('busqueda', '', type=str)
    id_categoria = request.args.get('categoria', None, type=int)
    id_marca = request.args.get('marca', None, type=int)
    activo = request.args.get('activo', None, type=str)
    
    # Convertir activo a bool si existe
    activo_filtro = None
    if activo == 'true':
        activo_filtro = True
    elif activo == 'false':
        activo_filtro = False
    
    # Construir filtros
    filtros = {}
    if busqueda:
        filtros['busqueda'] = busqueda
    if id_categoria:
        filtros['id_categoria'] = id_categoria
    if id_marca:
        filtros['id_marca'] = id_marca
    if activo_filtro is not None:
        filtros['activo'] = activo_filtro
    
    # Buscar
    paginacion = producto_service.buscar_admin(
        filtros=filtros,
        pagina=pagina,
        por_pagina=20
    )
    
    return render_template(
        'admin/productos/listado.html',
        productos=paginacion.items,
        paginacion=paginacion,
        busqueda=busqueda,
        id_categoria=id_categoria,
        id_marca=id_marca,
        activo=activo,
        categorias=categoria_service.obtener_todas(),
        marcas=marca_service.obtener_todas()
    )


@admin_bp.route('/productos/nuevo', methods=['GET', 'POST'])
@admin_required
def productos_nuevo():
    """Crear nuevo producto."""
    formulario = FormularioProducto()
    
    if formulario.validate_on_submit():
        try:
            producto_service.crear(
                codigo=formulario.codigo.data,
                nombre=formulario.nombre.data,
                id_categoria=formulario.id_categoria.data,
                id_marca=formulario.id_marca.data,
                precio_paquete_bs=formulario.precio_paquete_bs.data or 0,
                precio_docena_bs=formulario.precio_docena_bs.data or 0,
                precio_caja_bs=formulario.precio_caja_bs.data or 0,
                unidades_por_paquete=formulario.unidades_por_paquete.data,
                unidades_por_docena=formulario.unidades_por_docena.data or 12,
                unidades_por_caja=formulario.unidades_por_caja.data,
                descripcion=formulario.descripcion.data,
                url_imagen=formulario.url_imagen.data,
                activo=formulario.activo.data,
                visible_catalogo_publico=formulario.visible_catalogo_publico.data,
                mostrar_precio_paquete=formulario.mostrar_precio_paquete.data,
                mostrar_precio_docena=formulario.mostrar_precio_docena.data,
                mostrar_precio_caja=formulario.mostrar_precio_caja.data
            )
            flash('Producto creado correctamente.', 'success')
            return redirect(url_for('admin.productos_listado'))
        except ValueError as e:
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('admin/productos/formulario.html', form=formulario, producto=None)


@admin_bp.route('/productos/<int:id_producto>/editar', methods=['GET', 'POST'])
@admin_required
def productos_editar(id_producto):
    """Editar producto."""
    producto = producto_service.obtener_por_id(id_producto)
    if not producto:
        abort(404)
    
    # Pasar id_producto al formulario para validación de código único
    formulario = FormularioProducto(id_producto_edit=id_producto)
    
    if formulario.validate_on_submit():
        try:
            producto_service.actualizar(
                id_producto,
                codigo=formulario.codigo.data,
                nombre=formulario.nombre.data,
                id_categoria=formulario.id_categoria.data,
                id_marca=formulario.id_marca.data,
                precio_paquete_bs=formulario.precio_paquete_bs.data or 0,
                precio_docena_bs=formulario.precio_docena_bs.data or 0,
                precio_caja_bs=formulario.precio_caja_bs.data or 0,
                unidades_por_paquete=formulario.unidades_por_paquete.data,
                unidades_por_docena=formulario.unidades_por_docena.data or 12,
                unidades_por_caja=formulario.unidades_por_caja.data,
                descripcion=formulario.descripcion.data,
                url_imagen=formulario.url_imagen.data,
                activo=formulario.activo.data,
                visible_catalogo_publico=formulario.visible_catalogo_publico.data,
                mostrar_precio_paquete=formulario.mostrar_precio_paquete.data,
                mostrar_precio_docena=formulario.mostrar_precio_docena.data,
                mostrar_precio_caja=formulario.mostrar_precio_caja.data
            )
            flash('Producto actualizado correctamente.', 'success')
            return redirect(url_for('admin.productos_listado'))
        except ValueError as e:
            flash(f'Error: {str(e)}', 'danger')
    
    elif request.method == 'GET':
        # Llenar formulario con datos del producto
        formulario.codigo.data = producto.codigo
        formulario.nombre.data = producto.nombre
        formulario.id_categoria.data = producto.id_categoria
        formulario.id_marca.data = producto.id_marca
        formulario.precio_paquete_bs.data = producto.precio_paquete_bs
        formulario.precio_docena_bs.data = producto.precio_docena_bs
        formulario.precio_caja_bs.data = producto.precio_caja_bs
        formulario.unidades_por_paquete.data = producto.unidades_por_paquete
        formulario.unidades_por_docena.data = producto.unidades_por_docena
        formulario.unidades_por_caja.data = producto.unidades_por_caja
        formulario.descripcion.data = producto.descripcion
        formulario.url_imagen.data = producto.url_imagen
        formulario.activo.data = producto.activo
        formulario.visible_catalogo_publico.data = producto.visible_catalogo_publico
        formulario.mostrar_precio_paquete.data = producto.mostrar_precio_paquete
        formulario.mostrar_precio_docena.data = producto.mostrar_precio_docena
        formulario.mostrar_precio_caja.data = producto.mostrar_precio_caja
    
    return render_template('admin/productos/formulario.html', form=formulario, producto=producto)


@admin_bp.route('/productos/<int:id_producto>/eliminar', methods=['POST'])
@admin_required
def productos_eliminar(id_producto):
    """Eliminar producto."""
    if producto_service.eliminar(id_producto):
        flash('Producto eliminado correctamente.', 'success')
    else:
        flash('No se pudo eliminar el producto.', 'danger')
    
    return redirect(url_for('admin.productos_listado'))


# =====================
# CATEGORÍAS
# =====================

@admin_bp.route('/categorias')
@admin_required
def categorias_listado():
    """Listado de categorías."""
    categorias = categoria_service.obtener_todas()
    return render_template('admin/categorias/listado.html', categorias=categorias)


@admin_bp.route('/categorias/nueva', methods=['GET', 'POST'])
@admin_required
def categorias_nueva():
    """Crear nueva categoría."""
    formulario = FormularioCategoria()
    
    if formulario.validate_on_submit():
        try:
            categoria_service.crear(
                nombre=formulario.nombre.data,
                descripcion=formulario.descripcion.data or None
            )
            flash('Categoría creada correctamente.', 'success')
            return redirect(url_for('admin.categorias_listado'))
        except ValueError as e:
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('admin/categorias/formulario.html', form=formulario, categoria=None)


@admin_bp.route('/categorias/<int:id_categoria>/editar', methods=['GET', 'POST'])
@admin_required
def categorias_editar(id_categoria):
    """Editar categoría."""
    categoria = categoria_service.obtener_por_id(id_categoria)
    if not categoria:
        abort(404)
    
    formulario = FormularioCategoria()
    
    if formulario.validate_on_submit():
        try:
            categoria_service.actualizar(
                id_categoria,
                nombre=formulario.nombre.data,
                descripcion=formulario.descripcion.data or None,
                activo=formulario.activo.data
            )
            flash('Categoría actualizada correctamente.', 'success')
            return redirect(url_for('admin.categorias_listado'))
        except ValueError as e:
            flash(f'Error: {str(e)}', 'danger')
    
    elif request.method == 'GET':
        formulario.nombre.data = categoria.nombre
        formulario.descripcion.data = categoria.descripcion
        formulario.activo.data = categoria.activo
    
    return render_template('admin/categorias/formulario.html', form=formulario, categoria=categoria)


@admin_bp.route('/categorias/<int:id_categoria>/eliminar', methods=['POST'])
@admin_required
def categorias_eliminar(id_categoria):
    """Eliminar categoría."""
    if categoria_service.eliminar(id_categoria):
        flash('Categoría eliminada correctamente.', 'success')
    else:
        flash('No se puede eliminar: la categoría tiene productos asociados.', 'warning')
    
    return redirect(url_for('admin.categorias_listado'))


# =====================
# MARCAS
# =====================

@admin_bp.route('/marcas')
@admin_required
def marcas_listado():
    """Listado de marcas."""
    marcas = marca_service.obtener_todas()
    return render_template('admin/marcas/listado.html', marcas=marcas)


@admin_bp.route('/marcas/nueva', methods=['GET', 'POST'])
@admin_required
def marcas_nueva():
    """Crear nueva marca."""
    formulario = FormularioMarca()
    
    if formulario.validate_on_submit():
        try:
            marca_service.crear(
                nombre=formulario.nombre.data,
                descripcion=formulario.descripcion.data or None
            )
            flash('Marca creada correctamente.', 'success')
            return redirect(url_for('admin.marcas_listado'))
        except ValueError as e:
            flash(f'Error: {str(e)}', 'danger')
    
    return render_template('admin/marcas/formulario.html', form=formulario, marca=None)


@admin_bp.route('/marcas/<int:id_marca>/editar', methods=['GET', 'POST'])
@admin_required
def marcas_editar(id_marca):
    """Editar marca."""
    marca = marca_service.obtener_por_id(id_marca)
    if not marca:
        abort(404)
    
    formulario = FormularioMarca()
    
    if formulario.validate_on_submit():
        try:
            marca_service.actualizar(
                id_marca,
                nombre=formulario.nombre.data,
                descripcion=formulario.descripcion.data or None,
                activo=formulario.activo.data
            )
            flash('Marca actualizada correctamente.', 'success')
            return redirect(url_for('admin.marcas_listado'))
        except ValueError as e:
            flash(f'Error: {str(e)}', 'danger')
    
    elif request.method == 'GET':
        formulario.nombre.data = marca.nombre
        formulario.descripcion.data = marca.descripcion
        formulario.activo.data = marca.activo
    
    return render_template('admin/marcas/formulario.html', form=formulario, marca=marca)


@admin_bp.route('/marcas/<int:id_marca>/eliminar', methods=['POST'])
@admin_required
def marcas_eliminar(id_marca):
    """Eliminar marca."""
    if marca_service.eliminar(id_marca):
        flash('Marca eliminada correctamente.', 'success')
    else:
        flash('No se puede eliminar: la marca tiene productos asociados.', 'warning')
    
    return redirect(url_for('admin.marcas_listado'))
