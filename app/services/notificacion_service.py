"""
Servicio de Notificaciones - LibroVivo
Envio de correos y notificaciones internas
"""
from datetime import datetime, timedelta
from app.config import Config
from app.models.notificacion import Notificacion
from app.models.prestamo import Prestamo
from app.utils.email_sender import enviar_email


def crear_notificacion_recordatorio(prestamo):
    """
    Crea una notificacion de recordatorio de vencimiento
    
    Args:
        prestamo: Datos del prestamo
    
    Returns:
        int: ID de la notificacion
    """
    dias_restantes = (prestamo['fecha_devolucion_prevista'] - datetime.now()).days
    
    if dias_restantes == Config.DIAS_RECORDATORIO:
        mensaje = f"Recordatorio: El libro '{prestamo['libro_titulo']}' vence en {dias_restantes} dias. Devuelvelo antes del {prestamo['fecha_devolucion_prevista'].strftime('%d/%m/%Y')}."
    elif dias_restantes < 0:
        mensaje = f"ATENCION: El libro '{prestamo['libro_titulo']}' vencio hace {abs(dias_restantes)} dias. Devuelvelo lo antes posible para evitar multas."
    else:
        mensaje = f"El libro '{prestamo['libro_titulo']}' vence manana. No olvides devolverlo."
    
    return Notificacion.crear(
        prestamo['usuario_id'],
        'recordatorio',
        mensaje,
        prestamo['id']
    )


def enviar_recordatorios_vencimiento():
    """
    Envia recordatorios de vencimiento a usuarios
    Se ejecuta diariamente
    
    Returns:
        list: Notificaciones creadas
    """
    # Obtener prestamos que vencen en 2 dias
    prestamos = Prestamo.listar_vencen_hoy_o_mañana(Config.DIAS_RECORDATORIO)
    
    notificaciones = []
    
    for prestamo in prestamo:
        notificacion_id = crear_notificacion_recordatorio(prestamo)
        
        if notificacion_id:
            # Enviar email si esta configurado
            if Config.MAIL_USERNAME and prestamo.get('email'):
                enviar_email(
                    destinatario=prestamo['email'],
                    asunto=f"Recordatorio - LibroVivo: '{prestamo['libro_titulo']}'",
                    mensaje=f"""
                    Hola {prestamo['usuario_nombre']},
                    
                    {Notificacion.obtener_por_id(notificacion_id)['mensaje']}
                    
                    Gracias por usar LibroVivo.
                    """
                )
                Notificacion.marcar_email_enviado(notificacion_id)
            
            notificaciones.append({
                'notificacion_id': notificacion_id,
                'usuario': f"{prestamo['usuario_nombre']} {prestamo['usuario_apellido']}",
                'libro': prestamo['libro_titulo']
            })
    
    return notificaciones


def enviar_notificacion_reserva_disponible(reserva):
    """
    Envia notificacion cuando un libro reservado esta disponible
    
    Args:
        reserva: Datos de la reserva
    
    Returns:
        bool: True si se envio correctamente
    """
    mensaje = f"¡Buenas noticias! El libro '{reserva['libro_titulo']}' que reservaste ya esta disponible. Tienes hasta el {reserva['fecha_vencimiento'].strftime('%d/%m/%Y')} para retirarlo de la biblioteca."
    
    Notificacion.crear(
        reserva['usuario_id'],
        'reserva_disponible',
        mensaje,
        reserva['id']
    )
    
    # Enviar email
    if Config.MAIL_USERNAME and reserva.get('email'):
        enviar_email(
            destinatario=reserva['email'],
            asunto=f"Libro Disponible - LibroVivo: '{reserva['libro_titulo']}'",
            mensaje=f"""
            Hola {reserva['usuario_nombre']},
            
            {mensaje}
            
            Horario de atencion: Lunes a Viernes de 7:00 AM a 5:00 PM
            
            Gracias por usar LibroVivo.
            """
        )
    
    return True


def obtener_notificaciones_usuario(usuario_id, limite=10):
    """
    Obtiene las notificaciones de un usuario
    
    Args:
        usuario_id: ID del usuario
        limite: Cantidad maxima de notificaciones
    
    Returns:
        list: Notificaciones
    """
    return Notificacion.listar_por_usuario(usuario_id, limite=limite)


def marcar_notificacion_leida(notificacion_id):
    """
    Marca una notificacion como leida
    
    Args:
        notificacion_id: ID de la notificacion
    
    Returns:
        bool: True si se marco correctamente
    """
    return Notificacion.marcar_leida(notificacion_id)


def contar_notificaciones_no_leidas(usuario_id):
    """
    Cuenta las notificaciones no leidas de un usuario
    
    Args:
        usuario_id: ID del usuario
    
    Returns:
        int: Cantidad de notificaciones no leidas
    """
    return Notificacion.contar_no_leidas(usuario_id)