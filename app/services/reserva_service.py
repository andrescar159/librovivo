"""
Servicio de Reservas - LibroVivo
Logica de negocio para reservas de libros
"""
from datetime import datetime, timedelta
from app.config import Config
from app.models.reserva import Reserva
from app.models.libro import Libro
from app.models.ejemplar import Ejemplar
from app.models.notificacion import Notificacion


def validar_limite_reservas(usuario_id):
    """
    Valida que el usuario no exceda el limite de reservas activas
    
    Returns:
        tuple: (valido: bool, mensaje: str)
    """
    activas = Reserva.contar_activas_por_usuario(usuario_id)
    
    if activas >= Config.MAX_RESERVAS_ACTIVAS:
        return False, f"Has alcanzado el limite de {Config.MAX_RESERVAS_ACTIVAS} reservas activas"
    
    return True, f"Tienes {activas} de {Config.MAX_RESERVAS_ACTIVAS} reservas activas"


def validar_libro_reservable(libro_id):
    """
    Valida que el libro exista y tenga ejemplares prestables
    
    Returns:
        tuple: (valido: bool, mensaje: str)
    """
    libro = Libro.obtener_por_id(libro_id)
    
    if not libro:
        return False, "Libro no encontrado"
    
    if not libro['activo']:
        return False, "El libro no esta disponible"
    
    # Verificar que tenga al menos un ejemplar prestable
    ejemplares = Ejemplar.listar_por_libro(libro_id, activo=True)
    ejemplares_prestables = [e for e in ejemplares if e['es_prestable']]
    
    if not ejemplares_prestables:
        return False, "Este libro no tiene ejemplares disponibles para prestamo"
    
    return True, "Libro reservable"


def validar_reserva_unica(libro_id, usuario_id):
    """
    Valida que el usuario no tenga ya una reserva activa del mismo libro
    
    Returns:
        tuple: (valido: bool, mensaje: str)
    """
    if Reserva.usuario_tiene_reserva_activa(libro_id, usuario_id):
        return False, "Ya tienes una reserva activa para este libro"
    
    return True, "Puedes reservar este libro"


def calcular_fecha_vencimiento_reserva():
    """
    Calcula la fecha de vencimiento de una reserva
    
    Returns:
        datetime: Fecha de vencimiento
    """
    return datetime.now() + timedelta(days=Config.DIAS_RESERVA)


def crear_reserva(libro_id, usuario_id):
    """
    Crea una nueva reserva con todas las validaciones
    
    Args:
        libro_id: ID del libro a reservar
        usuario_id: ID del estudiante
    
    Returns:
        tuple: (exito: bool, mensaje: str, reserva_id: int)
    """
    # Validar limite de reservas
    valido, mensaje = validar_limite_reservas(usuario_id)
    if not valido:
        return False, mensaje, None
    
    # Validar libro
    valido, mensaje = validar_libro_reservable(libro_id)
    if not valido:
        return False, mensaje, None
    
    # Validar reserva unica
    valido, mensaje = validar_reserva_unica(libro_id, usuario_id)
    if not valido:
        return False, mensaje, None
    
    # Calcular fecha de vencimiento
    fecha_vencimiento = calcular_fecha_vencimiento_reserva()
    
    # Crear reserva
    reserva_id = Reserva.crear(libro_id, usuario_id, fecha_vencimiento)
    
    if reserva_id:
        return True, f"Reserva creada exitosamente. Tienes hasta el {fecha_vencimiento.strftime('%d/%m/%Y')} para retirar el libro", reserva_id
    
    return False, "Error al crear la reserva", None


def cancelar_reserva(reserva_id, usuario_id):
    """
    Cancela una reserva
    
    Args:
        reserva_id: ID de la reserva
        usuario_id: ID del usuario (para validar)
    
    Returns:
        tuple: (exito: bool, mensaje: str)
    """
    reserva = Reserva.obtener_por_id(reserva_id)
    
    if not reserva:
        return False, "Reserva no encontrada"
    
    if reserva['usuario_id'] != usuario_id:
        return False, "No puedes cancelar una reserva que no es tuya"
    
    if reserva['estado'] != 'activa':
        return False, f"La reserva ya fue {reserva['estado']}"
    
    if Reserva.cancelar(reserva_id):
        return True, "Reserva cancelada exitosamente"
    
    return False, "Error al cancelar la reserva"


def procesar_reservas_vencidas():
    """
    Marca como vencidas las reservas que pasaron la fecha limite
    Se ejecuta periodicamente
    
    Returns:
        int: Cantidad de reservas vencidas
    """
    Reserva.marcar_vencidas()
    vencidas = Reserva.listar_vencidas()
    return len(vencidas)


def notificar_reservas_disponibles():
    """
    Notifica a usuarios cuando su libro reservado esta disponible
    
    Returns:
        list: Notificaciones enviadas
    """
    reservas = Reserva.listar_disponibles_para_notificar()
    notificaciones = []
    
    for reserva in reservas:
        mensaje = f"El libro '{reserva['libro_titulo']}' que reservaste ya esta disponible. Tienes hasta el {reserva['fecha_vencimiento'].strftime('%d/%m/%Y')} para retirarlo."
        
        Notificacion.crear(
            reserva['usuario_id'],
            'reserva_disponible',
            mensaje,
            reserva['id']
        )
        
        Reserva.marcar_notificacion_enviada(reserva['id'])
        
        notificaciones.append({
            'reserva_id': reserva['id'],
            'usuario': f"{reserva['usuario_nombre']} {reserva['usuario_apellido']}",
            'libro': reserva['libro_titulo']
        })
    
    return notificaciones


def completar_reserva(reserva_id):
    """
    Marca una reserva como completada cuando el usuario retira el libro
    
    Args:
        reserva_id: ID de la reserva
    
    Returns:
        tuple: (exito: bool, mensaje: str)
    """
    reserva = Reserva.obtener_por_id(reserva_id)
    
    if not reserva:
        return False, "Reserva no encontrada"
    
    if reserva['estado'] != 'activa':
        return False, f"La reserva ya fue {reserva['estado']}"
    
    if Reserva.completar(reserva_id):
        return True, "Reserva completada. El libro ha sido retirado"
    
    return False, "Error al completar la reserva"