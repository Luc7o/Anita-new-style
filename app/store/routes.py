from flask import render_template, request, redirect, url_for, flash, session
from app.store import store_bp
from app.models import Producto, Categoria, Promocion, ProductoEnPromocion
from app import db


# ============================================
# HOME
# ============================================
@store_bp.route('/')
def home():
    # Productos destacados
    destacados = Producto.query.filter_by(activo=True, destacado=True).limit(8).all()
    
    # Productos nuevos
    nuevos = Producto.query.filter_by(activo=True).order_by(Producto.fecha_creacion.desc()).limit(8).all()
    
    # Categorías activas
    categorias = Categoria.query.filter_by(activa=True).order_by(Categoria.orden).all()
    
    # Promociones vigentes destacadas
    from datetime import date
    hoy = date.today()
    promociones = Promocion.query.filter(
        Promocion.activa == True,
        Promocion.destacada == True,
        Promocion.fecha_inicio <= hoy,
        Promocion.fecha_fin >= hoy
    ).limit(3).all()

    return render_template('store/home.html',
        destacados=destacados,
        nuevos=nuevos,
        categorias=categorias,
        promociones=promociones
    )


# ============================================
# CATÁLOGO
# ============================================
@store_bp.route('/catalogo')
def catalogo():
    page        = request.args.get('page', 1, type=int)
    genero      = request.args.get('genero', '')
    categoria   = request.args.get('categoria', '')
    orden       = request.args.get('orden', 'nuevo')
    busqueda    = request.args.get('q', '')
    precio_min  = request.args.get('precio_min', 0, type=float)
    precio_max  = request.args.get('precio_max', 9999, type=float)

    query = Producto.query.filter_by(activo=True)

    if genero:
        query = query.filter(Producto.genero == genero)
    if categoria:
        cat = Categoria.query.filter_by(slug=categoria).first()
        if cat:
            query = query.filter(Producto.categoria_id == cat.id)
    if busqueda:
        query = query.filter(Producto.nombre.ilike(f'%{busqueda}%'))
    if precio_min:
        query = query.filter(Producto.precio >= precio_min)
    if precio_max < 9999:
        query = query.filter(Producto.precio <= precio_max)

    if orden == 'precio_asc':
        query = query.order_by(Producto.precio.asc())
    elif orden == 'precio_desc':
        query = query.order_by(Producto.precio.desc())
    elif orden == 'nombre':
        query = query.order_by(Producto.nombre.asc())
    else:
        query = query.order_by(Producto.fecha_creacion.desc())

    productos   = query.paginate(page=page, per_page=12, error_out=False)
    categorias  = Categoria.query.filter_by(activa=True).order_by(Categoria.orden).all()

    return render_template('store/catalogo.html',
        productos=productos,
        categorias=categorias,
        genero=genero,
        categoria=categoria,
        orden=orden,
        busqueda=busqueda,
        precio_min=precio_min,
        precio_max=precio_max
    )


# ============================================
# DETALLE PRODUCTO
# ============================================
@store_bp.route('/producto/<slug>')
def detalle_producto(slug):
    producto = Producto.query.filter_by(slug=slug, activo=True).first_or_404()
    
    # Variantes
    variantes_colores = db.session.query(
        ProductoEnPromocion.producto_id
    ).filter_by(producto_id=producto.id).all()

    # Productos relacionados (misma categoría)
    relacionados = Producto.query.filter(
        Producto.categoria_id == producto.categoria_id,
        Producto.id != producto.id,
        Producto.activo == True
    ).limit(4).all()

    # Promoción vigente del producto
    from datetime import date
    hoy = date.today()
    promo = db.session.query(ProductoEnPromocion).join(Promocion).filter(
        ProductoEnPromocion.producto_id == producto.id,
        Promocion.activa == True,
        Promocion.fecha_inicio <= hoy,
        Promocion.fecha_fin >= hoy
    ).first()

    return render_template('store/detalle_producto.html',
        producto=producto,
        relacionados=relacionados,
        promo=promo
    )


# ============================================
# CATEGORÍA
# ============================================
@store_bp.route('/categoria/<slug>')
def categoria(slug):
    cat         = Categoria.query.filter_by(slug=slug, activa=True).first_or_404()
    page        = request.args.get('page', 1, type=int)
    orden       = request.args.get('orden', 'nuevo')

    query = Producto.query.filter_by(categoria_id=cat.id, activo=True)

    if orden == 'precio_asc':
        query = query.order_by(Producto.precio.asc())
    elif orden == 'precio_desc':
        query = query.order_by(Producto.precio.desc())
    else:
        query = query.order_by(Producto.fecha_creacion.desc())

    productos   = query.paginate(page=page, per_page=12, error_out=False)
    categorias  = Categoria.query.filter_by(activa=True).order_by(Categoria.orden).all()

    return render_template('store/categoria.html',
        categoria=cat,
        productos=productos,
        categorias=categorias,
        orden=orden
    )


# ============================================
# BÚSQUEDA
# ============================================
@store_bp.route('/buscar')
def buscar():
    q       = request.args.get('q', '')
    page    = request.args.get('page', 1, type=int)

    productos = Producto.query.filter(
        Producto.nombre.ilike(f'%{q}%'),
        Producto.activo == True
    ).paginate(page=page, per_page=12, error_out=False)

    return render_template('store/buscar.html',
        productos=productos,
        busqueda=q
    )


# ============================================
# PROMOCIONES
# ============================================
@store_bp.route('/promociones')
def promociones():
    from datetime import date
    hoy = date.today()
    
    promos = Promocion.query.filter(
        Promocion.activa == True,
        Promocion.fecha_inicio <= hoy,
        Promocion.fecha_fin >= hoy
    ).all()

    return render_template('store/promociones.html', promociones=promos)