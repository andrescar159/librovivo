"""
Servicio de Autenticación - LibroVivo
"""
import bcrypt
from flask import session
from app.models.usuario import Usuario
from app.config import Config


def validar_credenciales(email, password):
    """
    Valida las credenciales de un usuario
    
    Args:
        email: Correo electronico
        password: Contrasena en texto plano
    
    Returns:
        dict: Datos del usuario si es valido, None si no
    """
    usuario = Usuario.obtener_por_email(email)
    
    if not usuario:
        return None
    
    # Verificar contrasena con bcrypt
    if bcrypt.checkpw(password.encode('utf-8'), usuario.password_hash.encode('utf-8')):
        return {
            'id': usuario.id,
            'nombre': usuario.nombre,
            'apellido': usuario.apellido,
            'email': usuario.email,
            'rol': usuario.rol,
            'foto_perfil': usuario.foto_perfil
        }
    
    return None


def crear_sesion(usuario_data):
    """
    Crea la sesion del usuario en Flask
    
    Args:
        usuario_data: Diccionario con datos del usuario
    """
    session['usuario_id'] = usuario_data['id']
    session['nombre'] = f"{usuario_data['nombre']} {usuario_data['apellido']}"
    session['email'] = usuario_data['email']
    session['rol'] = usuario_data['rol']
    session['foto_perfil'] = usuario_data.get('foto_perfil')
    session.permanent = True


def cerrar_sesion():
    """Cierra la sesion del usuario"""
    session.clear()


def esta_autenticado():
    """Verifica si hay un usuario autenticado"""
    return 'usuario_id' in session


def obtener_rol():
    """Obtiene el rol del usuario autenticado"""
    return session.get('rol', None)


def obtener_usuario_id():
    """Obtiene el ID del usuario autenticado"""
    return session.get('usuario_id', None)


def es_admin():
    """Verifica si el usuario es administrador"""
    return session.get('rol') == 'admin'


def es_bibliotecario():
    """Verifica si el usuario es bibliotecario"""
    return session.get('rol') == 'bibliotecario'


def es_estudiante():
    """Verifica si el usuario es estudiante"""
    return session.get('rol') == 'estudiante'


def tiene_permiso(roles_permitidos):
    """
    Verifica si el usuario tiene uno de los roles permitidos
    
    Args:
        roles_permitidos: Lista de roles permitidos ['admin', 'bibliotecario']
    
    Returns:
        bool: True si tiene permiso
    """
    rol = session.get('rol')
    return rol in roles_permitidos if isinstance(roles_permitidos, list) else rol == roles_permitidos


def hash_password(password):
    """
    Genera un hash seguro de la contrasena
    
    Args:
        password: Contrasena en texto plano
    
    Returns:
        str: Hash de la contrasena
    """
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')


def verificar_password(password, password_hash):
    """
    Verifica una contrasena contra su hash
    
    Args:
        password: Contrasena en texto plano
        password_hash: Hash almacenado
    
    Returns:
        bool: True si coincide
    """
    return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))


def cambiar_password(usuario_id, password_actual, password_nueva):
    """
    Cambia la contrasena de un usuario
    
    Args:
        usuario_id: ID del usuario
        password_actual: Contrasena actual
        password_nueva: Nueva contrasena
    
    Returns:
        tuple: (exito: bool, mensaje: str)
    """
    usuario = Usuario.obtener_por_id(usuario_id)
    
    if not usuario:
        return False, "Usuario no encontrado"
    
    if not verificar_password(password_actual, usuario.password_hash):
        return False, "Contrasena actual incorrecta"
    
    nuevo_hash = hash_password(password_nueva)
    
    if Usuario.cambiar_password(usuario_id, nuevo_hash):
        return True, "Contrasena cambiada exitosamente"
    
    return False, "Error al cambiar la contrasena"


def generar_password_temporal():
    """Genera una contrasena temporal segura"""
    import secrets
    import string
    
    caracteres = string.ascii_letters + string.digits
    return ''.join(secrets.choice(caracteres) for _ in range(12))
