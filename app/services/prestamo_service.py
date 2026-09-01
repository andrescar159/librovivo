"""
Servicio de Prestamos - LibroVivo
Logica de negocio para prestamos, devoluciones y renovaciones
"""
from datetime import datetime, timedelta
from app.config import Config
from app.models.prestamo import Prestamo
from app.models.ejemplar import Ejemplar
from app.models.multa import Multa
from app.models.usuario import Usuario
from app.services.multa_service import calcular_multa, crear_multa


def validar_horario_biblioteca():
    """
    Valida si la biblioteca esta abierta
    
    Returns:
        tuple: (valido: bool, mensaje: str)
    """
    ahora = datetime.now()
    hora = ahora.hour
    
    if hora < Config.HORARIO_APERTURA or hora >= Config.HORARIO_CIERRE:
        return False, f"La biblioteca solo atiende de {Config.HORARIO_APERTURA}:00 a {Config.HORARIO_CIERRE}:00"
    
    return True, "Horario valido"


def validar_limite_prestamos(usuario_id):
    """
    Valida que el usuario no exceda el limite de prestamos
    
    Returns:
        tuple: (valido: bool, mensaje: str)
    """
    activos = Prestamo.contar_activos_por_usuario(usuario_id)
    
    if activos >= Config.MAX_PRESTAMOS_ESTUDIANTE:
        return False, f"Has alcanzado el limite de {Config.MAX_PRESTAMOS_ESTUDIANTE} prestamos activos"
    
    return True, f"Tienes {activos} de {Config.MAX_PRESTAMOS_ESTUDIANTE} prestamos"


def validar_multas_pendientes(usuario_id):
    """
    Valida que el usuario no tenga multas pendientes
    
    Returns:
        tuple: (valido: bool, mensaje: str)
    """
    if Multa.tiene_multas_pendientes(usuario_id):
        multas = Multa.contar_pendientes_por_usuario(usuario_id)
        return False, f"Tienes {multas['total']} multa(s) pendiente(s) por ${multas['total_monto']:,.0f} COP"
    
    return True, "Sin multas pendientes"


def validar_ejemplar_disponible(ejemplar_id):
    """
    Valida que el ejemplar este disponible para prestamo
    
    Returns:
        tuple: (valido: bool, mensaje: str)
    """
    ejemplar = Ejemplar.obtener_por_id(ejemplar_id)
    
    if not ejemplar:
        return False, "Ejemplar no encontrado"
    
    if not ejemplar['activo']:
        return False, "El ejemplar no esta activo"
    
    if ejemplar['estado'] != 'disponible':
        return False, f"El ejemplar no esta disponible (estado: {ejemplar['estado']})"
    
    if not ejemplar['es_prestable']:
        return False, "Este ejemplar es de consulta en sala unicamente"
    
    return True, "Ejemplar disponible"


def calcular_fecha_devolucion(dias=None):
    """
    Calcula la fecha de devolucion prevista
    
    Args:
        dias: Dias de prestamo (default: Config.DIAS_PRESTAMO)
    
    Returns:
        datetime: Fecha de devolucion
    """
    dias = dias or Config.DIAS_PRESTAMO
    return datetime.now() + timedelta(days=dias)


def crear_prestamo(ejemplar_id, usuario_id, bibliotecario_id):
    """
    Crea un nuevo prestamo con todas las validaciones
    
    Args:
        ejemplar_id: ID del ejemplar
        usuario_id: ID del estudiante
        bibliotecario_id: ID del bibliotecario que registra
    
    Returns:
        tuple: (exito: bool, mensaje: str, prestamo_id: int)
    """
    # Validar horario
    valido, mensaje = validar_horario_biblioteca()
    if not valido:
        return False, mensaje, None
    
    # Validar limite de prestamos
    valido, mensaje = validar_limite_prestamos(usuario_id)
    if not valido:
        return False, mensaje, None
    
    # Validar multas pendientes
    valido, mensaje = validar_multas_pendientes(usuario_id)
    if not valido:
        return False, mensaje, None
    
    # Validar ejemplar
    valido, mensaje = validar_ejemplar_disponible(ejemplar_id)
    if not valido:
        return False, mensaje, None
    
    # Calcular fecha de devolucion
    fecha_devolucion = calcular_fecha_devolucion()
    
    # Crear prestamo
    prestamo_id = Prestamo.crear(ejemplar_id, usuario_id, bibliotecario_id, fecha_devolucion)
    
    if prestamo_id:
        # Cambiar estado del ejemplar
        Ejemplar.cambiar_estado(ejemplar_id, 'prestado')
        return True, f"Prestamo creado exitosamente. Devolver antes del {fecha_devolucion.strftime('%d/%m/%Y')}", prestamo_id
    
    return False, "Error al crear el prestamo", None


def devolver_prestamo(prestamo_id, bibliotecario_id, observaciones=None):
    """
    Procesa la devolucion de un prestamo
    
    Args:
        prestamo_id: ID del prestamo
        bibliotecario_id: ID del bibliotecario que recibe
        observaciones: Notas opcionales
    
    Returns:
        tuple: (exito: bool, mensaje: str, multa_generada: dict)
    """
    prestamo = Prestamo.obtener_por_id(prestamo_id)
    
    if not prestamo:
        return False, "Prestamo no encontrado", None
    
    if prestamo['estado'] != 'activo':
        return False, f"El prestamo ya fue {prestamo['estado']}", None
    
    # Registrar devolucion
    Prestamo.devolver(prestamo_id, observaciones)
    
    # Cambiar estado del ejemplar
    Ejemplar.cambiar_estado(prestamo['ejemplar_id'], 'disponible')
    
    # Verificar si hay retraso y generar multa
    multa_info = None
    hoy = datetime.now()
    fecha_prevista = prestamo['fecha_devolucion_prevista']
    
    if isinstance(fecha_prevista, str):
        fecha_prevista = datetime.strptime(fecha_prevista, '%Y-%m-%d %H:%M:%S')
    
    if hoy > fecha_prevista:
        dias_retraso = (hoy - fecha_prevista).days
        monto = calcular_multa(dias_retraso)
        
        multa_id = crear_multa(prestamo_id, prestamo['usuario_id'], dias_retraso, monto)
        
        if multa_id:
            multa_info = {
                'id': multa_id,
                'dias_retraso': dias_retraso,
                'monto': monto
            }
            return True, f"Devolucion registrada. Multa generada: ${monto:,.0f} COP por {dias_retraso} dia(s) de retraso", multa_info
    
    return True, "Devolucion registrada exitosamente. Sin multas", None


def renovar_prestamo(prestamo_id, usuario_id):
    """
    Renueva un prestamo
    
    Args:
        prestamo_id: ID del prestamo
        usuario_id: ID del usuario (para validar)
    
    Returns:
        tuple: (exito: bool, mensaje: str)
    """
    prestamo = Prestamo.obtener_por_id(prestamo_id)
    
    if not prestamo:
        return False, "Prestamo no encontrado"
    
    if prestamo['usuario_id'] != usuario_id:
        return False, "No puedes renovar un prestamo que no es tuyo"
    
    if prestamo['estado'] != 'activo':
        return False, f"El prestamo ya fue {prestamo['estado']}"
    
    if prestamo['renovaciones_usadas'] >= Config.MAX_RENOVACIONES:
        return False, f"Has alcanzado el limite de {Config.MAX_RENOVACIONES} renovaciones"
    
    # Verificar que no este vencido
    hoy = datetime.now()
    fecha_prevista = prestamo['fecha_devolucion_prevista']
    
    if isinstance(fecha_prevista, str):
        fecha_prevista = datetime.strptime(fecha_prevista, '%Y-%m-%d %H:%M:%S')
    
    if hoy > fecha_prevista:
        return False, "No puedes renovar un prestamo vencido. Debes devolverlo primero"
    
    # Verificar que no haya reservas pendientes para este libro
    from app.models.reserva import Reserva
    reservas = Reserva.listar_activas()
    for reserva in reservas:
        if reserva['libro_id'] == prestamo['libro_id']:
            return False, "No se puede renovar: hay una reserva activa para este libro"
    
    # Calcular nueva fecha
    nueva_fecha = calcular_fecha_devolucion()
    
    if Prestamo.renovar(prestamo_id, nueva_fecha):
        return True, f"Prestamo renovado. Nueva fecha de devolucion: {nueva_fecha.strftime('%d/%m/%Y')}"
    
    return False, "Error al renovar el prestamo"


def extender_prestamo_bibliotecario(prestamo_id, bibliotecario_id, dias=2):
    """
    Extiende un prestamo por parte del bibliotecario (max 2 dias)
    
    Args:
        prestamo_id: ID del prestamo
        bibliotecario_id: ID del bibliotecario
        dias: Dias de extension (max 2)
    
    Returns:
        tuple: (exito: bool, mensaje: str)
    """
    if dias > Config.DIAS_EXTENSION_BIBLIOTECARIO:
        return False, f"La extension maxima es de {Config.DIAS_EXTENSION_BIBLIOTECARIO} dias"
    
    prestamo = Prestamo.obtener_por_id(prestamo_id)
    
    if not prestamo:
        return False, "Prestamo no encontrado"
    
    if prestamo['estado'] != 'activo':
        return False, f"El prestamo ya fue {prestamo['estado']}"
    
    # Calcular nueva fecha sumando dias a la fecha actual prevista
    fecha_actual = prestamo['fecha_devolucion_prevista']
    if isinstance(fecha_actual, str):
        fecha_actual = datetime.strptime(fecha_actual, '%Y-%m-%d %H:%M:%S')
    
    nueva_fecha = fecha_actual + timedelta(days=dias)
    
    if Prestamo.renovar(prestamo_id, nueva_fecha):
        return True, f"Prestamo extendido hasta: {nueva_fecha.strftime('%d/%m/%Y')}"
    
    return False, "Error al extender el prestamo"


def obtener_estadisticas_dashboard():
    """
    Obtiene estadisticas para el dashboard del admin
    
    Returns:
        dict: Estadisticas varias
    """
    from app.models.usuario import Usuario
    from app.models.libro import Libro
    
    hoy = datetime.now()
    
    return {
        'total_usuarios': Usuario.contar(activo=True),
        'total_libros': Libro.contar(activo=True),
        'prestamos_activos': len(Prestamo.listar_activos(por_pagina=1000)),
        'prestamos_vencidos': len(Prestamo.listar_vencidos()),
        'multas_pendientes': len(Multa.listar_pendientes(por_pagina=1000)),
        'total_recaudado': Multa.total_recaudado(),
        'prestamos_mes': Prestamo.contar_prestamos_mes(hoy.month, hoy.year),
        'libros_mas_prestados': Libro.mas_prestados(5)
    }
