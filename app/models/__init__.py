"""
Modelos SQLAlchemy para la aplicación NBF Listados.
Mapean exactamente con el esquema SQL Server existente.
"""

from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import check_password_hash
from app.extensions import db


class Usuario(UserMixin, db.Model):
    """
    Modelo de usuario para autenticación y autorización.
    Tabla: Usuario
    """
    __tablename__ = 'Usuario'
    
    id_usuario = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(150), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    rol = db.Column(db.String(20), nullable=False, default='ADMIN')  # ADMIN o EDITOR
    activo = db.Column(db.Boolean, nullable=False, default=True)
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ultimo_login = db.Column(db.DateTime, nullable=True)
    
    # Relaciones
    historial_ediciones = db.relationship('HistorialEdicion', back_populates='usuario', lazy='dynamic')
    
    def get_id(self):
        """Necesario para Flask-Login."""
        return self.id_usuario
    
    def check_password(self, password):
        """Verificar contraseña con hash."""
        return check_password_hash(self.password_hash, password)
    
    def es_admin(self):
        """¿Es administrador?"""
        return self.rol == 'ADMIN' and self.activo
    
    def es_editor(self):
        """¿Es editor?"""
        return self.rol == 'EDITOR' and self.activo
    
    def __repr__(self):
        return f'<Usuario {self.email}>'


class Categoria(db.Model):
    """
    Modelo de categoría de productos.
    Tabla: Categoria
    """
    __tablename__ = 'Categoria'
    
    id_categoria = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True, index=True)
    descripcion = db.Column(db.String(255), nullable=True)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relaciones
    productos = db.relationship('Producto', back_populates='categoria', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Categoria {self.nombre}>'


class Marca(db.Model):
    """
    Modelo de marca de productos.
    Tabla: Marca
    """
    __tablename__ = 'Marca'
    
    id_marca = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True, index=True)
    descripcion = db.Column(db.String(255), nullable=True)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relaciones
    productos = db.relationship('Producto', back_populates='marca', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Marca {self.nombre}>'


class Producto(db.Model):
    """
    Modelo de producto.
    Tabla: Producto
    """
    __tablename__ = 'Producto'
    
    id_producto = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(50), nullable=False, unique=True, index=True)
    nombre = db.Column(db.String(150), nullable=False, index=True)
    descripcion = db.Column(db.String(255), nullable=True)
    url_imagen = db.Column(db.String(500), nullable=True)
    
    # Claves foráneas
    id_categoria = db.Column(db.Integer, db.ForeignKey('Categoria.id_categoria'), nullable=False, index=True)
    id_marca = db.Column(db.Integer, db.ForeignKey('Marca.id_marca'), nullable=False, index=True)
    
    # Precios en Bs (bolivianos)
    precio_paquete_bs = db.Column(db.Numeric(18, 2), nullable=False, default=0)
    precio_docena_bs = db.Column(db.Numeric(18, 2), nullable=False, default=0)
    precio_caja_bs = db.Column(db.Numeric(18, 2), nullable=False, default=0)
    
    # Unidades
    unidades_por_paquete = db.Column(db.Integer, nullable=True)
    unidades_por_docena = db.Column(db.Integer, nullable=False, default=12)
    unidades_por_caja = db.Column(db.Integer, nullable=False)
    
    # Estado
    activo = db.Column(db.Boolean, nullable=False, default=True, index=True)
    visible_catalogo_publico = db.Column(db.Boolean, nullable=False, default=True)
    
    # Controlar qué precios mostrar
    mostrar_precio_paquete = db.Column(db.Boolean, nullable=False, default=False)
    mostrar_precio_docena = db.Column(db.Boolean, nullable=False, default=False)
    mostrar_precio_caja = db.Column(db.Boolean, nullable=False, default=False)
    
    # Auditoría
    fecha_creacion = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    categoria = db.relationship('Categoria', back_populates='productos')
    marca = db.relationship('Marca', back_populates='productos')
    
    def obtener_imagen_url(self):
        """Retornar URL de imagen o placeholder si no existe."""
        if self.url_imagen:
            return self.url_imagen
        return 'https://via.placeholder.com/300x300?text=Sin+imagen'
    
    def obtener_precios_visibles(self):
        """Retornar dict con precios visibles."""
        precios = {}
        if self.mostrar_precio_paquete and self.unidades_por_paquete:
            precios['paquete'] = {
                'precio': float(self.precio_paquete_bs),
                'unidades': self.unidades_por_paquete
            }
        if self.mostrar_precio_docena:
            precios['docena'] = {
                'precio': float(self.precio_docena_bs),
                'unidades': self.unidades_por_docena
            }
        if self.mostrar_precio_caja:
            precios['caja'] = {
                'precio': float(self.precio_caja_bs),
                'unidades': self.unidades_por_caja
            }
        return precios
    
    def es_visible_publico(self):
        """¿Se ve en catálogo público?"""
        return self.activo and self.visible_catalogo_publico
    
    def __repr__(self):
        return f'<Producto {self.codigo}:{self.nombre}>'


class HistorialEdicion(db.Model):
    """
    Modelo para auditoría de cambios en productos (opcional, para futuro).
    """
    __tablename__ = 'HistorialEdicion'
    
    id_edicion = db.Column(db.Integer, primary_key=True)
    id_producto = db.Column(db.Integer, db.ForeignKey('Producto.id_producto'), nullable=False)
    id_usuario = db.Column(db.Integer, db.ForeignKey('Usuario.id_usuario'), nullable=False)
    cambio = db.Column(db.String(500), nullable=False)
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relaciones
    usuario = db.relationship('Usuario', back_populates='historial_ediciones')
    
    def __repr__(self):
        return f'<Edicion producto={self.id_producto} por={self.id_usuario}>'
