"""
Inicializacion de la aplicacion Flask - LibroVivo
"""
from flask import Flask
from app.config import config


def create_app(config_name='default'):
    """Factory pattern para crear la aplicacion Flask"""
    app = Flask(
        __name__,
        template_folder='templates',
        static_folder='static'
    )
    
    # Cargar configuracion
    app.config.from_object(config[config_name])
    
    # Registrar blueprints
    from app.routes.auth import auth_bp
    from app.routes.dashboard import dashboard_bp
    from app.routes.usuarios import usuarios_bp
    from app.routes.libros import libros_bp
    from app.routes.prestamos import prestamos_bp
    from app.routes.multas import multas_bp
    from app.routes.reservas import reservas_bp
    from app.routes.resenas import resenas_bp
    from app.routes.reportes import reportes_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(dashboard_bp, url_prefix='/dashboard')
    app.register_blueprint(usuarios_bp, url_prefix='/usuarios')
    app.register_blueprint(libros_bp, url_prefix='/libros')
    app.register_blueprint(prestamos_bp, url_prefix='/prestamos')
    app.register_blueprint(multas_bp, url_prefix='/multas')
    app.register_blueprint(reservas_bp, url_prefix='/reservas')
    app.register_blueprint(resenas_bp, url_prefix='/resenas')
    app.register_blueprint(reportes_bp, url_prefix='/reportes')
    
    # Ruta principal redirige al login
    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('auth.login'))
    
    # Manejadores de error
    @app.errorhandler(404)
    def not_found(error):
        from flask import render_template
        return render_template('errores/404.html'), 404
    
    @app.errorhandler(403)
    def forbidden(error):
        from flask import render_template
        return render_template('errores/403.html'), 403
    
    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        return render_template('errores/500.html'), 500
    
    # Context processor para variables globales en templates
    @app.context_processor
    def inject_globals():
        from flask import session
        return {
            'app_name': app.config['APP_NAME'],
            'app_version': app.config['APP_VERSION'],
            'usuario_rol': session.get('rol', None),
            'usuario_nombre': session.get('nombre', None)
        }
    
    return app
