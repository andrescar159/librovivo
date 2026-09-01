"""
Decoradores personalizados - LibroVivo
Proteccion de rutas segun roles de usuario
"""
from functools import wraps
from flask import session, redirect, url_for, flash


def login_required(f):
    """
    Decorador que requiere que el usuario este autenticado
    
    Uso:
        @app.route('/ruta-protegida')
        @login_required
        def ruta_protegida():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Debes iniciar sesion para acceder a esta pagina', 'warning')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def admin_required(f):
    """
    Decorador que requiere rol de administrador
    
    Uso:
        @app.route('/admin')
        @admin_required
        def panel_admin():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Debes iniciar sesion', 'warning')
            return redirect(url_for('auth.login'))
        
        if session.get('rol') != 'admin':
            flash('No tienes permisos de administrador', 'danger')
            return redirect(url_for('dashboard.index'))
        
        return f(*args, **kwargs)
    return decorated_function


def bibliotecario_required(f):
    """
    Decorador que requiere rol de bibliotecario o admin
    
    Uso:
        @app.route('/prestamos')
        @bibliotecario_required
        def gestionar_prestamos():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Debes iniciar sesion', 'warning')
            return redirect(url_for('auth.login'))
        
        if session.get('rol') not in ['admin', 'bibliotecario']:
            flash('No tienes permisos para esta accion', 'danger')
            return redirect(url_for('dashboard.index'))
        
        return f(*args, **kwargs)
    return decorated_function


def estudiante_required(f):
    """
    Decorador que requiere rol de estudiante (o admin/bibliotecario)
    
    Uso:
        @app.route('/mis-prestamos')
        @estudiante_required
        def mis_prestamos():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' not in session:
            flash('Debes iniciar sesion', 'warning')
            return redirect(url_for('auth.login'))
        
        # Admin y bibliotecario tambien pueden acceder
        if session.get('rol') not in ['admin', 'bibliotecario', 'estudiante']:
            flash('Rol no valido', 'danger')
            return redirect(url_for('dashboard.index'))
        
        return f(*args, **kwargs)
    return decorated_function


def no_autenticado(f):
    """
    Decorador que redirige si el usuario YA esta autenticado
    Util para la pagina de login
    
    Uso:
        @app.route('/login')
        @no_autenticado
        def login():
            ...
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'usuario_id' in session:
            return redirect(url_for('dashboard.index'))
        return f(*args, **kwargs)
    return decorated_function