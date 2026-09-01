"""
Rutas de Usuarios - LibroVivo
CRUD de usuarios (solo admin y bibliotecario)
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.utils.decorators import login_required, admin_required, bibliotecario_required
from app.services.auth_service import hash_password, generar_password_temporal
from app.models.usuario import Usuario
from app.models.prestamo import Prestamo
from app.models.multa import Multa
from app.utils.helpers import validar_email, validar_documento, validar_telefono, guardar_archivo

usuarios_bp = Blueprint('usuarios', __name__)


@usuarios_bp.route('/')
@login_required
def lista():
    """
    Lista de usuarios
    """
    # Solo admin ve todos, bibliotecario solo ve estudiantes
    if session.get('rol') == 'admin':
        rol_filtro = request.args.get('rol', None)
        usuarios = Usuario.listar_todos(rol=rol_filtro, activo=True, por_pagina=1000)
    else:
        usuarios = Usuario.listar_todos(rol='estudiante', activo=True, por_pagina=1000)
    
    return render_template('usuarios/lista.html', usuarios=usuarios)


@usuarios_bp.route('/crear', methods=['GET', 'POST'])
@bibliotecario_required
def crear():
    """
    Crear nuevo usuario
    """
    if request.method == 'POST':
        # Obtener datos del formulario
        nombre = request.form.get('nombre', '').strip()
        apellido = request.form.get('apellido', '').strip()
        email = request.form.get('email', '').strip()
        rol = request.form.get('rol', 'estudiante')
        documento = request.form.get('documento', '').strip()
        telefono = request.form.get('telefono', '').strip()
        
        # Validaciones
        if not nombre or not apellido or not email:
            flash('Nombre, apellido y correo son obligatorios', 'warning')
            return render_template('usuarios/crear.html')
        
        if not validar_email(email):
            flash('El correo electronico no es valido', 'warning')
            return render_template('usuarios/crear.html')
        
        # Verificar que el email no exista
        if Usuario.obtener_por_email(email):
            flash('Ya existe un usuario con este correo', 'warning')
            return render_template('usuarios/crear.html')
        
        # Validar documento si se proporciono
        if documento and not validar_documento(documento):
            flash('El documento no es valido (solo numeros, 6-12 digitos)', 'warning')
            return render_template('usuarios/crear.html')
        
        # Validar telefono si se proporciono
        if telefono and not validar_telefono(telefono):
            flash('El telefono no es valido', 'warning')
            return render_template('usuarios/crear.html')
        
        # Validar rol (bibliotecario no puede crear admins)
        if session.get('rol') == 'bibliotecario' and rol == 'admin':
            flash('No tienes permisos para crear administradores', 'danger')
            return render_template('usuarios/crear.html')
        
        # Generar contrasena temporal
        password_temporal = generar_password_temporal()
        password_hash = hash_password(password_temporal)
        
        # Procesar foto de perfil
        foto_perfil = None
        if 'foto_perfil' in request.files:
            archivo = request.files['foto_perfil']
            if archivo.filename:
                foto_perfil = guardar_archivo(archivo, 'perfiles')
        
        # Crear usuario
        usuario_id = Usuario.crear(
            nombre=nombre,
            apellido=apellido,
            email=email,
            password_hash=password_hash,
            rol=rol,
            documento=documento or None,
            telefono=telefono or None,
            foto_perfil=foto_perfil
        )
        
        if usuario_id:
            # Enviar correo de bienvenida
            from app.utils.email_sender import enviar_bienvenida
            enviar_bienvenida(email, nombre, password_temporal)
            
            flash(f'Usuario creado exitosamente. Contrasena temporal: {password_temporal}', 'success')
            return redirect(url_for('usuarios.lista'))
        else:
            flash('Error al crear el usuario', 'danger')
    
    return render_template('usuarios/crear.html')


@usuarios_bp.route('/<int:usuario_id>')
@login_required
def ver(usuario_id):
    """
    Ver detalle de un usuario
    """
    usuario = Usuario.obtener_por_id(usuario_id)
    
    if not usuario:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('usuarios.lista'))
    
    # Validar permisos
    if session.get('rol') == 'bibliotecario' and usuario.rol != 'estudiante':
        flash('No puedes ver este usuario', 'danger')
        return redirect(url_for('usuarios.lista'))
    
    # Obtener datos relacionados
    prestamos = Prestamo.listar_por_usuario(usuario_id)
    multas = Multa.listar_por_usuario(usuario_id)
    
    return render_template('usuarios/ver.html',
                         usuario=usuario,
                         prestamos=prestamos,
                         multas=multas)


@usuarios_bp.route('/<int:usuario_id>/editar', methods=['GET', 'POST'])
@bibliotecario_required
def editar(usuario_id):
    """
    Editar usuario
    """
    usuario = Usuario.obtener_por_id(usuario_id)
    
    if not usuario:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('usuarios.lista'))
    
    # Validar permisos
    if session.get('rol') == 'bibliotecario' and usuario.rol != 'estudiante':
        flash('No puedes editar este usuario', 'danger')
        return redirect(url_for('usuarios.lista'))
    
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        apellido = request.form.get('apellido', '').strip()
        telefono = request.form.get('telefono', '').strip()
        activo = request.form.get('activo') == 'on'
        
        # Solo admin puede cambiar el rol
        datos = {
            'nombre': nombre,
            'apellido': apellido,
            'telefono': telefono or None,
            'activo': 1 if activo else 0
        }
        
        if session.get('rol') == 'admin':
            rol = request.form.get('rol')
            if rol:
                datos['rol'] = rol
        
        # Procesar foto de perfil
        if 'foto_perfil' in request.files:
            archivo = request.files['foto_perfil']
            if archivo.filename:
                # Eliminar foto anterior
                if usuario.foto_perfil:
                    from app.utils.helpers import eliminar_archivo
                    eliminar_archivo(usuario.foto_perfil)
                
                foto_perfil = guardar_archivo(archivo, 'perfiles')
                datos['foto_perfil'] = foto_perfil
        
        if Usuario.actualizar(usuario_id, **datos):
            flash('Usuario actualizado exitosamente', 'success')
            return redirect(url_for('usuarios.ver', usuario_id=usuario_id))
        else:
            flash('Error al actualizar el usuario', 'danger')
    
    return render_template('usuarios/editar.html', usuario=usuario)


@usuarios_bp.route('/<int:usuario_id>/eliminar', methods=['POST'])
@admin_required
def eliminar(usuario_id):
    """
    Eliminar (desactivar) usuario
    """
    # No permitir eliminar el propio usuario
    if usuario_id == session.get('usuario_id'):
        flash('No puedes eliminar tu propio usuario', 'danger')
        return redirect(url_for('usuarios.lista'))
    
    usuario = Usuario.obtener_por_id(usuario_id)
    
    if not usuario:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('usuarios.lista'))
    
    if Usuario.eliminar(usuario_id):
        flash('Usuario desactivado exitosamente', 'success')
    else:
        flash('Error al desactivar el usuario', 'danger')
    
    return redirect(url_for('usuarios.lista'))


@usuarios_bp.route('/<int:usuario_id>/reset-password', methods=['POST'])
@bibliotecario_required
def reset_password(usuario_id):
    """
    Restablecer contrasena de un usuario
    """
    usuario = Usuario.obtener_por_id(usuario_id)
    
    if not usuario:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('usuarios.lista'))
    
    # Validar permisos
    if session.get('rol') == 'bibliotecario' and usuario.rol != 'estudiante':
        flash('No puedes modificar este usuario', 'danger')
        return redirect(url_for('usuarios.lista'))
    
    # Generar nueva contrasena
    nueva_password = generar_password_temporal()
    nuevo_hash = hash_password(nueva_password)
    
    if Usuario.cambiar_password(usuario_id, nuevo_hash):
        # Enviar correo
        from app.utils.email_sender import enviar_email
        enviar_email(
            destinatario=usuario.email,
            asunto='Contrasena Restablecida - LibroVivo',
            mensaje=f"""
            Hola {usuario.nombre},
            
            Tu contrasena ha sido restablecida.
            
            Tu nueva contrasena temporal es: {nueva_password}
            
            Por favor inicia sesion y cambiala lo antes posible.
            """
        )
        
        flash(f'Contrasena restablecida. Nueva contrasena: {nueva_password}', 'success')
    else:
        flash('Error al restablecer la contrasena', 'danger')
    
    return redirect(url_for('usuarios.ver', usuario_id=usuario_id))