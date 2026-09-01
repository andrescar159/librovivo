"""
Servicio de Multas - LibroVivo
Logica de negocio para calculo y gestion de multas
"""
from app.config import Config
from app.models.multa import Multa


def calcular_multa(dias_retraso):
    """
    Calcula el monto de la multa segun los dias de retraso
    
    Reglas:
    - $500 COP por dia de retraso
    - Maximo $7.000 COP (a los 10 dias)
    - Despues de 10 dias, se mantiene en $7.000
    
    Args:
        dias_retraso: Dias de retraso
    
    Returns:
        float: Monto de la multa
    """
    if dias_retraso <= 0:
        return 0
    
    monto = dias_retraso * Config.MULTA_POR_DIA
    
    # Aplicar limite maximo
    if monto > Config.MULTA_MAXIMA:
        monto = Config.MULTA_MAXIMA
    
    return monto


def crear_multa(prestamo_id, usuario_id, dias_retraso, monto=None):
    """
    Crea una multa por retraso
    
    Args:
        prestamo_id: ID del prestamo
        usuario_id: ID del usuario
        dias_retraso: Dias de retraso
        monto: Monto (opcional, se calcula si no se proporciona)
    
    Returns:
        int: ID de la multa creada
    """
    if monto is None:
        monto = calcular_multa(dias_retraso)
    
    return Multa.crear(prestamo_id, usuario_id, dias_retraso, monto)


def pagar_multa(multa_id, bibliotecario_id, observaciones=None):
    """
    Registra el pago de una multa
    
    Args:
        multa_id: ID de la multa
        bibliotecario_id: ID del bibliotecario que recibe el pago
        observaciones: Notas opcionales
    
    Returns:
        tuple: (exito: bool, mensaje: str)
    """
    multa = Multa.obtener_por_id(multa_id)
    
    if not multa:
        return False, "Multa no encontrada"
    
    if multa['estado'] == 'pagada':
        return False, "Esta multa ya fue pagada"
    
    if multa['estado'] == 'condonada':
        return False, "Esta multa fue condonada"
    
    if Multa.pagar(multa_id, observaciones):
        return True, f"Multa de ${multa['monto']:,.0f} COP pagada exitosamente"
    
    return False, "Error al registrar el pago"


def condonar_multa(multa_id, admin_id, observaciones=None):
    """
    Condona una multa (solo admin)
    
    Args:
        multa_id: ID de la multa
        admin_id: ID del admin que condona
        observaciones: Motivo de la condonacion
    
    Returns:
        tuple: (exito: bool, mensaje: str)
    """
    multa = Multa.obtener_por_id(multa_id)
    
    if not multa:
        return False, "Multa no encontrada"
    
    if multa['estado'] != 'pendiente':
        return False, f"Solo se pueden condonar multas pendientes (estado actual: {multa['estado']})"
    
    observacion_final = f"Condonada por admin ID {admin_id}"
    if observaciones:
        observacion_final += f". Motivo: {observaciones}"
    
    if Multa.condonar(multa_id, observacion_final):
        return True, f"Multa de ${multa['monto']:,.0f} COP condonada exitosamente"
    
    return False, "Error al condonar la multa"


def obtener_resumen_multas_usuario(usuario_id):
    """
    Obtiene un resumen de multas de un usuario
    
    Args:
        usuario_id: ID del usuario
    
    Returns:
        dict: Resumen de multas
    """
    pendientes = Multa.contar_pendientes_por_usuario(usuario_id)
    
    # Obtener historial
    sql = """
        SELECT estado, COUNT(*) as cantidad, SUM(monto) as total
        FROM multas 
        WHERE usuario_id = %s
        GROUP BY estado
    """
    from app.database import ejecutar_consulta
    resumen = ejecutar_consulta(sql, (usuario_id,), fetchall=True) or []
    
    return {
        'pendientes': pendientes['total'],
        'total_pendiente': pendientes['total_monto'] or 0,
        'detalle_por_estado': resumen
    }


def verificar_multas_vencidas():
    """
    Verifica prestamos vencidos y genera multas automaticamente
    Se ejecuta periodicamente (cron job)
    
    Returns:
        list: Multas generadas
    """
    from app.models.prestamo import Prestamo
    from datetime import datetime
    
    vencidos = Prestamo.listar_vencidos()
    multas_generadas = []
    
    for prestamo in vencidos:
        # Verificar si ya tiene multa
        sql = "SELECT id FROM multas WHERE prestamo_id = %s"
        from app.database import ejecutar_consulta
        existe = ejecutar_consulta(sql, (prestamo['id'],), fetchone=True)
        
        if not existe:
            # Calcular dias de retraso
            hoy = datetime.now()
            fecha_prevista = prestamo['fecha_devolucion_prevista']
            
            if isinstance(fecha_prevista, str):
                fecha_prevista = datetime.strptime(fecha_prevista, '%Y-%m-%d %H:%M:%S')
            
            dias_retraso = (hoy - fecha_prevista).days
            monto = calcular_multa(dias_retraso)
            
            multa_id = crear_multa(prestamo['id'], prestamo['usuario_id'], dias_retraso, monto)
            
            if multa_id:
                multas_generadas.append({
                    'multa_id': multa_id,
                    'prestamo_id': prestamo['id'],
                    'usuario': f"{prestamo['usuario_nombre']} {prestamo['usuario_apellido']}",
                    'dias_retraso': dias_retraso,
                    'monto': monto
                })
    
    return multas_generadas
