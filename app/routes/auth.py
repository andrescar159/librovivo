"""
Rutas de Autenticacion - LibroVivo
Login, logout y recuperacion de contrasena
"""
from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app.services.auth_service import (
    validar_credenciales, crear_sesion, cerrar_sesion, 
    hash_password, esta_autenticado
)
from app.utils.decorators import no_autenticado, login_required
from app.models.usuario import Usuario

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
@no_autenticado
def login():
    """
    Pagina de inicio de sesion
    """
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        # Validaciones basicas
        if not email or not password:
            flash('Por favor ingresa tu correo y contrasena', 'warning')
            return render_template('auth/login.html')
        
        # Validar credenciales
        usuario = validar_credenciales(email, password)
        
        if usuario:
            # Crear sesion
            crear_sesion(usuario)
            flash(f'Bienvenido, {usuario["nombre"]}!', 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash('Correo o contrasena incorrectos', 'danger')
    
    return render_template('auth/login.html')


@auth_bp.route('/logout')
@login_required
def logout():
    """
    Cierra la sesion del usuario
    """
    cerrar_sesion()
    flash('Has cerrado sesion exitosamente', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        apellido = request.form.get('apellido')
        email = request.form.get('email')
        documento = request.form.get('documento')
        telefono = request.form.get('telefono')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
        
        # Validaciones
        if not all([nombre, apellido, email, password]):
            flash('Todos los campos obligatorios deben completarse', 'error')
            return redirect(url_for('auth.registro'))
        
        if password != password_confirm:
            flash('Las contrasenas no coinciden', 'error')
            return redirect(url_for('auth.registro'))
        
        if len(password) < 8:
            flash('La contrasena debe tener al menos 8 caracteres', 'error')
            return redirect(url_for('auth.registro'))
        
        # Verificar si el email ya existe
        if Usuario.obtener_por_email(email):
            flash('Este correo ya esta registrado', 'error')
            return redirect(url_for('auth.registro'))
        
        # Crear usuario (inactivo por defecto, admin debe activar)
        from app.services.auth_service import hash_password
        password_hash = hash_password(password)
        
        Usuario.crear(
            nombre=nombre,
            apellido=apellido,
            email=email,
            password_hash=password_hash,
            rol='estudiante',
            documento=documento,
            telefono=telefono,
            activo=False  # Inactivo hasta que admin lo active
        )
        
        flash('Registro exitoso. Tu cuenta sera activada por un administrador.', 'success')
        return redirect(url_for('auth.login'))
    
    return render_template('auth/registro.html')

@auth_bp.route('/recuperar-password', methods=['GET', 'POST'])
@no_autenticado
def recuperar_password():
    """
    Pagina de recuperacion de contrasena
    """
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        
        if not email:
            flash('Por favor ingresa tu correo electronico', 'warning')
            return render_template('auth/recuperar_password.html')
        
        # Verificar si el usuario existe
        usuario = Usuario.obtener_por_email(email)
        
        if usuario:
            # Generar nueva contrasena temporal
            from app.services.auth_service import generar_password_temporal
            nueva_password = generar_password_temporal()
            nuevo_hash = hash_password(nueva_password)
            
            # Actualizar contrasena
            if Usuario.cambiar_password(usuario.id, nuevo_hash):
                # Enviar correo con nueva contrasena
                from app.utils.email_sender import enviar_email
                enviar_email(
                    destinatario=email,
                    asunto='Recuperacion de Contrasena - LibroVivo',
                    mensaje=f"""
                    Hola {usuario.nombre},
                    
                    Has solicitado recuperar tu contrasena.
                    
                    Tu nueva contrasena temporal es: {nueva_password}
                    
                    Por favor inicia sesion y cambiala lo antes posible.
                    
                    Si no solicitaste este cambio, contacta al administrador.
                    """
                )
                
                flash('Se ha enviado una nueva contrasena a tu correo', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash('Error al generar la nueva contrasena', 'danger')
        else:
            # No revelar si el correo existe o no (seguridad)
            flash('Si el correo existe en nuestro sistema, recibiras instrucciones', 'info')
            return redirect(url_for('auth.login'))
    
    return render_template('auth/recuperar_password.html')


@auth_bp.route('/cambiar-password', methods=['GET', 'POST'])
@login_required
def cambiar_password():
    """
    Pagina para cambiar la contrasena (usuario autenticado)
    """
    if request.method == 'POST':
        password_actual = request.form.get('password_actual', '')
        password_nueva = request.form.get('password_nueva', '')
        password_confirmar = request.form.get('password_confirmar', '')
        
        # Validaciones
        if not password_actual or not password_nueva or not password_confirmar:
            flash('Todos los campos son obligatorios', 'warning')
            return render_template('auth/cambiar_password.html')
        
        if password_nueva != password_confirmar:
            flash('Las contrasenas nuevas no coinciden', 'warning')
            return render_template('auth/cambiar_password.html')
        
        if len(password_nueva) < 8:
            flash('La contrasena nueva debe tener al menos 8 caracteres', 'warning')
            return render_template('auth/cambiar_password.html')
        
        # Cambiar contrasena
        from app.services.auth_service import cambiar_password
        exito, mensaje = cambiar_password(session['usuario_id'], password_actual, password_nueva)
        
        if exito:
            flash(mensaje, 'success')
            return redirect(url_for('dashboard.index'))
        else:
            flash(mensaje, 'danger')
    
    return render_template('auth/cambiar_password.html')