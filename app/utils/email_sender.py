"""
Envio de correos electronicos - LibroVivo
Utiliza smtplib para enviar notificaciones por email
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.config import Config


def enviar_email(destinatario, asunto, mensaje, html=False):
    """
    Envia un correo electronico
    
    Args:
        destinatario: Correo del destinatario
        asunto: Asunto del correo
        mensaje: Contenido del correo
        html: True si el mensaje es HTML
    
    Returns:
        bool: True si se envio correctamente
    """
    # Verificar configuracion
    if not Config.MAIL_USERNAME or not Config.MAIL_PASSWORD:
        print("Error: Configuracion de correo incompleta")
        return False
    
    try:
        # Crear mensaje
        msg = MIMEMultipart()
        msg['From'] = Config.MAIL_DEFAULT_SENDER
        msg['To'] = destinatario
        msg['Subject'] = f"{Config.APP_NAME} - {asunto}"
        
        # Adjuntar contenido
        if html:
            msg.attach(MIMEText(mensaje, 'html'))
        else:
            msg.attach(MIMEText(mensaje, 'plain'))
        
        # Conectar y enviar
        server = smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT)
        server.starttls()
        server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        
        return True
        
    except Exception as e:
        print(f"Error al enviar correo: {e}")
        return False


def enviar_recordatorio_prestamo(usuario_email, usuario_nombre, libro_titulo, fecha_vencimiento):
    """
    Envia recordatorio de vencimiento de prestamo
    
    Args:
        usuario_email: Correo del usuario
        usuario_nombre: Nombre del usuario
        libro_titulo: Titulo del libro
        fecha_vencimiento: Fecha de vencimiento
    
    Returns:
        bool: True si se envio correctamente
    """
    mensaje = f"""
    Hola {usuario_nombre},
    
    Te recordamos que el libro "{libro_titulo}" vence el {fecha_vencimiento}.
    
    Por favor devuelvelo a tiempo para evitar multas.
    
    Horario de atencion: Lunes a Viernes de {Config.HORARIO_APERTURA}:00 a {Config.HORARIO_CIERRE}:00
    
    Gracias por usar LibroVivo.
    """
    
    return enviar_email(
        destinatario=usuario_email,
        asunto=f"Recordatorio: Devolucion de '{libro_titulo}'",
        mensaje=mensaje
    )


def enviar_notificacion_reserva(usuario_email, usuario_nombre, libro_titulo, fecha_vencimiento):
    """
    Envia notificacion de reserva disponible
    
    Args:
        usuario_email: Correo del usuario
        usuario_nombre: Nombre del usuario
        libro_titulo: Titulo del libro
        fecha_vencimiento: Fecha limite de la reserva
    
    Returns:
        bool: True si se envio correctamente
    """
    mensaje = f"""
    Hola {usuario_nombre},
    
    ¡Buenas noticias! El libro "{libro_titulo}" que reservaste ya esta disponible.
    
    Tienes hasta el {fecha_vencimiento} para retirarlo de la biblioteca.
    
    Horario de atencion: Lunes a Viernes de {Config.HORARIO_APERTURA}:00 a {Config.HORARIO_CIERRE}:00
    
    Gracias por usar LibroVivo.
    """
    
    return enviar_email(
        destinatario=usuario_email,
        asunto=f"Libro Disponible: '{libro_titulo}'",
        mensaje=mensaje
    )


def enviar_bienvenida(usuario_email, usuario_nombre, password_temporal=None):
    """
    Envia correo de bienvenida a nuevos usuarios
    
    Args:
        usuario_email: Correo del usuario
        usuario_nombre: Nombre del usuario
        password_temporal: Contrasena temporal (opcional)
    
    Returns:
        bool: True si se envio correctamente
    """
    mensaje = f"""
    Hola {usuario_nombre},
    
    Bienvenido a LibroVivo - Sistema de Gestion Bibliotecaria.
    
    Tu cuenta ha sido creada exitosamente.
    """
    
    if password_temporal:
        mensaje += f"""
    
    Tu contrasena temporal es: {password_temporal}
    
    Por favor cambiala al iniciar sesion por primera vez.
    """
    
    mensaje += """
    
    Puedes acceder al sistema en: http://localhost:5000
    
    Gracias por unirte a LibroVivo.
    """
    
    return enviar_email(
        destinatario=usuario_email,
        asunto="Bienvenido a LibroVivo",
        mensaje=mensaje
    )