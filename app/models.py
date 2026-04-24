from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime


# ============================================
# LOADER DE USUARIO (Flask-Login)
# ============================================
@login_manager.user_loader
def load_user(user_id):
    return Usuario.query.get(int(user_id))


# ============================================
# MODELO: USUARIOS
# ============================================
class Usuario(UserMixin, db.Model):
    __tablename__ = 'usuarios'

    id                  = db.Column(db.Integer, primary_key=True)
    nombre              = db.Column(db.String(100), nullable=False)
    email               = db.Column(db.String(100), unique=True, nullable=False)
    contrasena          = db.Column('contraseña', db.String(255), nullable=False)
    telefono            = db.Column('teléfono', db.String(15))
    fecha_registro      = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_login        = db.Column('último_login', db.DateTime, nullable=True)
    activo              = db.Column(db.Boolean, default=True)
    token_recuperacion  = db.Column(db.String(100), nullable=True)

    # Relaciones
    direcciones         = db.relationship('DireccionUsuario', backref='usuario', lazy=True, cascade='all, delete-orphan')
    metodos_pago        = db.relationship('MetodoPago', backref='usuario', lazy=True, cascade='all, delete-orphan')
    carrito             = db.relationship('Carrito', backref='usuario', lazy=True, cascade='all, delete-orphan')
    ordenes             = db.relationship('Orden', backref='usuario', lazy=True)
    wishlist            = db.relationship('Wishlist', backref='usuario', lazy=True, cascade='all, delete-orphan')
    resenas             = db.relationship('ResenaProducto', backref='usuario', lazy=True, cascade='all, delete-orphan')
    historial_promo     = db.relationship('HistorialPromocionUsuario', backref='usuario', lazy=True)

    def __repr__(self):
        return f'<Usuario {self.email}>'


# ============================================
# MODELO: ADMINS
# ============================================
class Admin(UserMixin, db.Model):
    __tablename__ = 'admins'

    id              = db.Column(db.Integer, primary_key=True)
    nombre          = db.Column(db.String(100), nullable=False)
    email           = db.Column(db.String(100), unique=True, nullable=False)
    contrasena      = db.Column(db.String(255), nullable=False)
    rol             = db.Column(db.Enum('superadmin', 'editor', 'visor'), default='editor')
    activo          = db.Column(db.Boolean, default=True)
    ultimo_login    = db.Column(db.DateTime, nullable=True)
    fecha_creacion  = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Admin {self.email}>'

    def es_superadmin(self):
        return self.rol == 'superadmin'

    def puede_editar(self):
        return self.rol in ['superadmin', 'editor']


# ============================================
# MODELO: CATEGORÍAS
# ============================================
class Categoria(db.Model):
    __tablename__ = 'categorias'

    id              = db.Column(db.Integer, primary_key=True)
    nombre          = db.Column(db.String(100), unique=True, nullable=False)
    descripcion     = db.Column('descripción', db.Text)
    imagen          = db.Column(db.String(255))
    slug            = db.Column(db.String(100), unique=True)
    genero          = db.Column('género', db.Enum('dama', 'varón', 'infantil', 'unisex'), default='dama')
    orden           = db.Column(db.Integer, default=0)
    fecha_creacion  = db.Column('fecha_creación', db.DateTime, default=datetime.utcnow)
    activa          = db.Column(db.Boolean, default=True)

    # Relaciones
    productos       = db.relationship('Producto', backref='categoria', lazy=True)
    promociones     = db.relationship('Promocion', backref='categoria', lazy=True)

    def __repr__(self):
        return f'<Categoria {self.nombre}>'


# ============================================
# MODELO: PRODUCTOS
# ============================================
class Producto(db.Model):
    __tablename__ = 'productos'

    id                      = db.Column(db.Integer, primary_key=True)
    nombre                  = db.Column(db.String(150), nullable=False)
    slug                    = db.Column(db.String(150), unique=True)
    descripcion             = db.Column('descripción', db.Text, nullable=False)
    descripcion_larga       = db.Column('descripción_larga', db.Text)
    precio                  = db.Column(db.Numeric(10, 2), nullable=False)
    precio_original         = db.Column(db.Numeric(10, 2))
    categoria_id            = db.Column(db.Integer, db.ForeignKey('categorias.id'), nullable=False)
    genero                  = db.Column('género', db.Enum('dama', 'varón', 'infantil'), default='dama')
    subcategoria            = db.Column('subcategoría', db.String(100))
    stock                   = db.Column(db.Integer, default=0)
    peso                    = db.Column(db.Numeric(8, 3))
    dimensiones             = db.Column(db.String(50))
    material                = db.Column(db.String(100))
    sku                     = db.Column(db.String(50), unique=True, nullable=False)
    proveedor               = db.Column(db.String(100))
    imagen_principal        = db.Column(db.String(255))
    imagenes_adicionales    = db.Column(db.Text)
    es_destacado_temporada  = db.Column(db.Boolean, default=False)
    fecha_creacion          = db.Column('fecha_creación', db.DateTime, default=datetime.utcnow)
    fecha_actualizacion     = db.Column('fecha_actualización', db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    activo                  = db.Column(db.Boolean, default=True)
    destacado               = db.Column(db.Boolean, default=False)

    # Relaciones
    variantes       = db.relationship('VarianteProducto', backref='producto', lazy=True, cascade='all, delete-orphan')
    resenas         = db.relationship('ResenaProducto', backref='producto', lazy=True, cascade='all, delete-orphan')
    en_wishlist     = db.relationship('Wishlist', backref='producto', lazy=True, cascade='all, delete-orphan')
    en_carrito      = db.relationship('Carrito', backref='producto', lazy=True)
    en_promociones  = db.relationship('ProductoEnPromocion', backref='producto', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Producto {self.nombre}>'

    def tiene_stock(self):
        return self.stock > 0

    def precio_final(self):
        promo = ProductoEnPromocion.query.filter_by(producto_id=self.id).first()
        if promo:
            return promo.precio_promocional
        return self.precio


# ============================================
# MODELO: VARIANTES PRODUCTO
# ============================================
class VarianteProducto(db.Model):
    __tablename__ = 'variantes_producto'

    id                  = db.Column(db.Integer, primary_key=True)
    producto_id         = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    color               = db.Column(db.String(50))
    talla               = db.Column(db.String(20))
    stock               = db.Column(db.Integer, default=0)
    precio_adicional    = db.Column(db.Numeric(10, 2), default=0)
    sku_variante        = db.Column(db.String(50), unique=True)
    imagen              = db.Column(db.String(255))
    fecha_creacion      = db.Column('fecha_creación', db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Variante {self.color} - {self.talla}>'


# ============================================
# MODELO: PROMOCIONES
# ============================================
class Promocion(db.Model):
    __tablename__ = 'promociones'

    id                      = db.Column(db.Integer, primary_key=True)
    nombre                  = db.Column(db.String(150), nullable=False)
    slug                    = db.Column(db.String(100), unique=True)
    descripcion             = db.Column('descripción', db.Text)
    tipo                    = db.Column(db.Enum('porcentaje', 'cantidad_fija', 'envio_gratis', 'compra_x_lleva_y'), default='porcentaje')
    valor                   = db.Column(db.Numeric(10, 2))
    valor_minimo_compra     = db.Column('valor_mínimo_compra', db.Numeric(10, 2))
    fecha_inicio            = db.Column(db.Date, nullable=False)
    fecha_fin               = db.Column(db.Date, nullable=False)
    aplica_a                = db.Column(db.Enum('todos', 'dama', 'varón', 'infantil', 'categoria_específica'), default='todos')
    categoria_id            = db.Column('categoría_id', db.Integer, db.ForeignKey('categorias.id'), nullable=True)
    uso_maximo              = db.Column('uso_máximo', db.Integer)
    uso_actual              = db.Column(db.Integer, default=0)
    maximo_por_usuario      = db.Column('máximo_por_usuario', db.Integer, default=1)
    activa                  = db.Column(db.Boolean, default=True)
    destacada               = db.Column(db.Boolean, default=False)
    mostrar_en_productos    = db.Column(db.Boolean, default=True)
    imagen_banner           = db.Column(db.String(255))
    color_tema              = db.Column(db.String(20))
    fecha_creacion          = db.Column('fecha_creación', db.DateTime, default=datetime.utcnow)
    fecha_actualizacion     = db.Column('fecha_actualización', db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    cupones         = db.relationship('CuponTemporada', backref='promocion', lazy=True, cascade='all, delete-orphan')
    productos       = db.relationship('ProductoEnPromocion', backref='promocion', lazy=True, cascade='all, delete-orphan')
    historial       = db.relationship('HistorialPromocionUsuario', backref='promocion', lazy=True)

    def __repr__(self):
        return f'<Promocion {self.nombre}>'

    def esta_vigente(self):
        from datetime import date
        hoy = date.today()
        return self.activa and self.fecha_inicio <= hoy <= self.fecha_fin


# ============================================
# MODELO: PRODUCTOS EN PROMOCIÓN
# ============================================
class ProductoEnPromocion(db.Model):
    __tablename__ = 'productos_en_promoción'

    id                  = db.Column(db.Integer, primary_key=True)
    producto_id         = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    promocion_id        = db.Column('promoción_id', db.Integer, db.ForeignKey('promociones.id'), nullable=False)
    descuento_aplicado  = db.Column(db.Numeric(10, 2))
    precio_promocional  = db.Column(db.Numeric(10, 2))
    fecha_creacion      = db.Column('fecha_creación', db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ProductoEnPromocion prod={self.producto_id} promo={self.promocion_id}>'


# ============================================
# MODELO: CUPONES TEMPORADA
# ============================================
class CuponTemporada(db.Model):
    __tablename__ = 'cupones_temporada'

    id              = db.Column(db.Integer, primary_key=True)
    codigo          = db.Column('código', db.String(50), unique=True, nullable=False)
    promocion_id    = db.Column('promoción_id', db.Integer, db.ForeignKey('promociones.id'), nullable=False)
    descripcion     = db.Column('descripción', db.Text)
    tipo            = db.Column(db.Enum('automático', 'manual'), default='automático')
    descuento       = db.Column(db.Numeric(10, 2), nullable=False)
    tipo_descuento  = db.Column(db.Enum('porcentaje', 'cantidad_fija'), default='porcentaje')
    activo          = db.Column(db.Boolean, default=True)
    uso_maximo      = db.Column('uso_máximo', db.Integer)
    uso_actual      = db.Column(db.Integer, default=0)
    fecha_creacion  = db.Column('fecha_creación', db.DateTime, default=datetime.utcnow)

    # Relaciones
    historial       = db.relationship('HistorialPromocionUsuario', backref='cupon', lazy=True)

    def __repr__(self):
        return f'<Cupon {self.codigo}>'

    def es_valido(self):
        if not self.activo:
            return False
        if self.uso_maximo and self.uso_actual >= self.uso_maximo:
            return False
        return True


# ============================================
# MODELO: CARRITO
# ============================================
class Carrito(db.Model):
    __tablename__ = 'carrito'

    id              = db.Column(db.Integer, primary_key=True)
    usuario_id      = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    token_sesion    = db.Column('token_sesion', db.String(100))
    producto_id     = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    variante_id     = db.Column(db.Integer, db.ForeignKey('variantes_producto.id'), nullable=True)
    cantidad        = db.Column(db.Integer, default=1, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)
    fecha_anadido   = db.Column('fecha_añadido', db.DateTime, default=datetime.utcnow)

    # Relaciones
    variante        = db.relationship('VarianteProducto', backref='en_carrito', lazy=True)

    def __repr__(self):
        return f'<Carrito usuario={self.usuario_id} producto={self.producto_id}>'

    def subtotal(self):
        return self.cantidad * self.precio_unitario


# ============================================
# MODELO: DIRECCIONES USUARIO
# ============================================
class DireccionUsuario(db.Model):
    __tablename__ = 'direcciones_usuario'

    id                      = db.Column(db.Integer, primary_key=True)
    usuario_id              = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    tipo                    = db.Column(db.Enum('envio', 'facturacion'), default='envio')
    nombre                  = db.Column(db.String(100))
    nombre_completo         = db.Column(db.String(150), nullable=False)
    direccion               = db.Column('dirección', db.Text, nullable=False)
    numero_exterior         = db.Column('número_exterior', db.String(20))
    numero_interior         = db.Column('número_interior', db.String(20))
    apartado                = db.Column(db.String(50))
    ciudad                  = db.Column(db.String(50), nullable=False)
    provincia               = db.Column(db.String(50))
    codigo_postal           = db.Column('código_postal', db.String(10), nullable=False)
    pais                    = db.Column('país', db.String(50), default='PE')
    telefono                = db.Column('teléfono', db.String(15), nullable=False)
    instrucciones_entrega   = db.Column(db.Text)
    por_defecto             = db.Column(db.Boolean, default=False)
    fecha_creacion          = db.Column('fecha_creación', db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Direccion {self.ciudad} - {self.nombre_completo}>'


# ============================================
# MODELO: MÉTODOS DE PAGO
# ============================================
class MetodoPago(db.Model):
    __tablename__ = 'metodos_pago'

    id                  = db.Column(db.Integer, primary_key=True)
    usuario_id          = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    tipo                = db.Column(db.Enum('tarjeta_credito', 'paypal', 'transferencia', 'efectivo'), default='tarjeta_credito')
    ultimos_digitos     = db.Column(db.String(4))
    titular             = db.Column(db.String(150))
    fecha_vencimiento   = db.Column(db.String(7))
    email_paypal        = db.Column(db.String(100))
    por_defecto         = db.Column(db.Boolean, default=False)
    fecha_creacion      = db.Column('fecha_creación', db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<MetodoPago {self.tipo} usuario={self.usuario_id}>'


# ============================================
# MODELO: ÓRDENES
# ============================================
class Orden(db.Model):
    __tablename__ = 'ordenes'

    id                      = db.Column(db.Integer, primary_key=True)
    usuario_id              = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)
    numero_orden            = db.Column('número_orden', db.String(20), unique=True, nullable=False)
    subtotal                = db.Column(db.Numeric(10, 2), nullable=False)
    costo_envio             = db.Column('costo_envío', db.Numeric(10, 2), default=0)
    descuento               = db.Column(db.Numeric(10, 2), default=0)
    descuento_promocion     = db.Column('descuento_promoción', db.Numeric(10, 2), default=0)
    total                   = db.Column(db.Numeric(10, 2), nullable=False)
    estado                  = db.Column(db.Enum('pendiente', 'pagada', 'preparando', 'enviada', 'entregada', 'cancelada'), default='pendiente')
    direccion_envio         = db.Column('dirección_envío', db.Text, nullable=False)
    ciudad_envio            = db.Column('ciudad_envío', db.String(50), nullable=False)
    codigo_postal_envio     = db.Column('código_postal_envío', db.String(10))
    metodo_envio            = db.Column('método_envío', db.String(50))
    empresa_envio           = db.Column('empresa_envío', db.String(100))
    numero_seguimiento      = db.Column('número_seguimiento', db.String(100))
    metodo_pago             = db.Column('método_pago', db.Enum('tarjeta_credito', 'paypal', 'transferencia', 'efectivo'), default='tarjeta_credito')
    notas_cliente           = db.Column(db.Text)
    notas_admin             = db.Column(db.Text)
    fecha_orden             = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_pago              = db.Column(db.DateTime, nullable=True)
    fecha_envio             = db.Column('fecha_envío', db.DateTime, nullable=True)
    fecha_entrega           = db.Column(db.DateTime, nullable=True)
    fecha_actualizacion     = db.Column('fecha_actualización', db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relaciones
    detalles    = db.relationship('DetalleOrden', backref='orden', lazy=True, cascade='all, delete-orphan')
    envio       = db.relationship('Envio', backref='orden', lazy=True, uselist=False)
    historial   = db.relationship('HistorialPromocionUsuario', backref='orden', lazy=True)
    resenas     = db.relationship('ResenaProducto', backref='orden', lazy=True)

    def __repr__(self):
        return f'<Orden {self.numero_orden}>'


# ============================================
# MODELO: DETALLES ÓRDENES
# ============================================
class DetalleOrden(db.Model):
    __tablename__ = 'detalles_ordenes'

    id              = db.Column(db.Integer, primary_key=True)
    orden_id        = db.Column(db.Integer, db.ForeignKey('ordenes.id'), nullable=False)
    producto_id     = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    variante_id     = db.Column(db.Integer, db.ForeignKey('variantes_producto.id'), nullable=True)
    nombre_producto = db.Column(db.String(150), nullable=False)
    cantidad        = db.Column(db.Integer, nullable=False)
    precio_unitario = db.Column(db.Numeric(10, 2), nullable=False)

    # Relaciones
    producto        = db.relationship('Producto', backref='en_ordenes', lazy=True)
    variante        = db.relationship('VarianteProducto', backref='en_ordenes', lazy=True)

    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __repr__(self):
        return f'<DetalleOrden orden={self.orden_id} producto={self.producto_id}>'


# ============================================
# MODELO: ENVÍOS
# ============================================
class Envio(db.Model):
    __tablename__ = 'envios'

    id                      = db.Column(db.Integer, primary_key=True)
    orden_id                = db.Column(db.Integer, db.ForeignKey('ordenes.id'), nullable=False)
    empresa_envio           = db.Column('empresa_envío', db.String(100))
    numero_seguimiento      = db.Column('número_seguimiento', db.String(100), unique=True)
    estado                  = db.Column(db.Enum('preparando', 'recogida', 'en_tránsito', 'entregado', 'devuelto', 'cancelado'), default='preparando')
    ubicacion_actual        = db.Column('ubicación_actual', db.String(150))
    fecha_envio             = db.Column('fecha_envío', db.DateTime, nullable=True)
    fecha_entrega_estimada  = db.Column(db.Date)
    fecha_entrega_real      = db.Column(db.DateTime, nullable=True)
    costo                   = db.Column(db.Numeric(10, 2))
    peso                    = db.Column(db.Numeric(8, 3))
    fecha_creacion          = db.Column('fecha_creación', db.DateTime, default=datetime.utcnow)
    fecha_actualizacion     = db.Column('fecha_actualización', db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Envio orden={self.orden_id} estado={self.estado}>'


# ============================================
# MODELO: RESEÑAS Y CALIFICACIONES
# ============================================
class ResenaProducto(db.Model):
    __tablename__ = 'resenas_productos'

    id                  = db.Column(db.Integer, primary_key=True)
    producto_id         = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    usuario_id          = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    orden_id            = db.Column(db.Integer, db.ForeignKey('ordenes.id'), nullable=True)
    calificacion        = db.Column('calificación', db.Integer, nullable=False)
    titulo              = db.Column('título', db.String(150))
    contenido           = db.Column(db.Text)
    verificado          = db.Column(db.Boolean, default=False)
    utiles              = db.Column('útiles', db.Integer, default=0)
    fecha_creacion      = db.Column('fecha_creación', db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column('fecha_actualización', db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Resena producto={self.producto_id} cal={self.calificacion}>'


# ============================================
# MODELO: WISHLIST
# ============================================
class Wishlist(db.Model):
    __tablename__ = 'wishlist'

    id              = db.Column(db.Integer, primary_key=True)
    usuario_id      = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    producto_id     = db.Column(db.Integer, db.ForeignKey('productos.id'), nullable=False)
    fecha_anadido   = db.Column('fecha_añadido', db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Wishlist usuario={self.usuario_id} producto={self.producto_id}>'


# ============================================
# MODELO: HISTORIAL PROMOCIONES USUARIO
# ============================================
class HistorialPromocionUsuario(db.Model):
    __tablename__ = 'historial_promociones_usuario'

    id                  = db.Column(db.Integer, primary_key=True)
    usuario_id          = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    promocion_id        = db.Column('promoción_id', db.Integer, db.ForeignKey('promociones.id'), nullable=True)
    cupon_id            = db.Column('cupón_id', db.Integer, db.ForeignKey('cupones_temporada.id'), nullable=True)
    orden_id            = db.Column(db.Integer, db.ForeignKey('ordenes.id'), nullable=True)
    descuento_aplicado  = db.Column(db.Numeric(10, 2))
    fecha_uso           = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<HistorialPromo usuario={self.usuario_id}>'