"""
Rutas de Dashboard - LibroVivo
Dashboards personalizados por rol de usuario
"""
from flask import Blueprint, render_template, session
from app.utils.decorators import login_required
from app.services.prestamo_service import obtener_estadisticas_dashboard
from app.models.prestamo import Prestamo
from app.models.multa import Multa
from app.models.reserva import Reserva
from app.models.libro import Libro
from app.models.usuario import Usuario
from app.models.notificacion import Notificacion

dashboard_bp = Blueprint('dashboard', __name__)


@dashboard_bp.route('/')
@login_required
def index():
    """
    Redirige al dashboard correspondiente segun el rol del usuario
    """
    rol = session.get('rol')
    
    if rol == 'admin':
        return admin_dashboard()
    elif rol == 'bibliotecario':
        return bibliotecario_dashboard()
    else:  # estudiante
        return estudiante_dashboard()


def admin_dashboard():
    """
    Dashboard del administrador
    """
    # Estadisticas generales
    stats = obtener_estadisticas_dashboard()
    
    # Usuarios recientes
    usuarios_recientes = Usuario.listar_todos(activo=True, por_pagina=5)
    
    # Multas recientes
    multas_recientes = Multa.listar_todas(estado='pendiente', por_pagina=5)
    
    # Libros mas prestados
    libros_populares = Libro.mas_prestados(5)
    
    return render_template('dashboard/admin.html',
                         stats=stats,
                         usuarios_recientes=usuarios_recientes,
                         multas_recientes=multas_recientes,
                         libros_populares=libros_populares)


def bibliotecario_dashboard():
    """
    Dashboard del bibliotecario
    """
    # Prestamos activos
    prestamos_activos = Prestamo.listar_activos(por_pagina=1000)
    total_activos = len(prestamos_activos)
    
    # Devueltos hoy
    from datetime import datetime
    hoy = datetime.now().strftime('%Y-%m-%d')
    sql_hoy = """
        SELECT COUNT(*) as total FROM prestamos 
        WHERE DATE(fecha_devolucion_real) = %s AND estado = 'devuelto'
    """
    from app.database import ejecutar_consulta
    devueltos_hoy = ejecutar_consulta(sql_hoy, (hoy,), fetchone=True)
    devueltos_hoy = devueltos_hoy['total'] if devueltos_hoy else 0
    
    # Vencen manana
    vencen_proximos = Prestamo.listar_vencen_hoy_o_mañana(1)
    
    # Vencidos
    vencidos = Prestamo.listar_vencidos()
    
    # Reservas activas
    reservas_activas = Reserva.listar_activas()
    
    # Solicitudes de renovacion (prestamos activos con renovaciones usadas > 0)
    sql_renovaciones = """
        SELECT p.*, l.titulo as libro_titulo,
               u.nombre as usuario_nombre, u.apellido as usuario_apellido
        FROM prestamos p
        JOIN ejemplares e ON p.ejemplar_id = e.id
        JOIN libros l ON e.libro_id = l.id
        JOIN usuarios u ON p.usuario_id = u.id
        WHERE p.estado = 'activo' AND p.renovaciones_usadas > 0
        ORDER BY p.renovaciones_usadas DESC
        LIMIT 5
    """
    renovaciones = ejecutar_consulta(sql_renovaciones, fetchall=True) or []
    
    # Ejemplares no prestables
    sql_no_prestables = """
        SELECT e.*, l.titulo as libro_titulo
        FROM ejemplares e
        JOIN libros l ON e.libro_id = l.id
        WHERE e.es_prestable = FALSE AND e.activo = 1
        ORDER BY l.titulo
    """
    no_prestables = ejecutar_consulta(sql_no_prestables, fetchall=True) or []
    
    return render_template('dashboard/bibliotecario.html',
                         total_activos=total_activos,
                         devueltos_hoy=devueltos_hoy,
                         vencen_proximos=vencen_proximos,
                         vencidos=vencidos,
                         reservas_activas=reservas_activas,
                         renovaciones=renovaciones,
                         no_prestables=no_prestables)


def estudiante_dashboard():
    """
    Dashboard del estudiante
    """
    usuario_id = session['usuario_id']
    
    # Mis prestamos activos
    mis_prestamos = Prestamo.listar_por_usuario(usuario_id, estado='activo')
    
    # Mis reservas activas
    mis_reservas = Reserva.listar_por_usuario(usuario_id, estado='activa')
    
    # Multas pendientes
    mis_multas = Multa.contar_pendientes_por_usuario(usuario_id)
    
    # Notificaciones no leidas
    notificaciones = Notificacion.listar_por_usuario(usuario_id, solo_no_leidas=True, limite=5)
    total_notificaciones = Notificacion.contar_no_leidas(usuario_id)
    
    # Recomendaciones (libros de la misma categoria que los prestados)
    recomendaciones = []
    if mis_prestamos:
        categoria_ids = []
        for p in mis_prestamos:
            sql = """
                SELECT l.categoria_id FROM prestamos p
                JOIN ejemplares e ON p.ejemplar_id = e.id
                JOIN libros l ON e.libro_id = l.id
                WHERE p.id = %s
            """
            from app.database import ejecutar_consulta
            cat = ejecutar_consulta(sql, (p['id'],), fetchone=True)
            if cat and cat['categoria_id'] not in categoria_ids:
                categoria_ids.append(cat['categoria_id'])
        
        if categoria_ids:
            sql_rec = """
                SELECT l.*, c.nombre as categoria_nombre,
                       (SELECT AVG(calificacion) FROM resenas r WHERE r.libro_id = l.id AND r.activo = 1) as promedio
                FROM libros l
                LEFT JOIN categorias_dewey c ON l.categoria_id = c.id
                WHERE l.categoria_id IN (%s) AND l.activo = 1
                ORDER BY promedio DESC
                LIMIT 4
            """ % ','.join(['%s'] * len(categoria_ids))
            recomendaciones = ejecutar_consulta(sql_rec, tuple(categoria_ids), fetchall=True) or []
    
    # Libros populares
    populares = Libro.mas_prestados(5)
    
    return render_template('dashboard/estudiante.html',
                         mis_prestamos=mis_prestamos,
                         mis_reservas=mis_reservas,
                         mis_multas=mis_multas,
                         notificaciones=notificaciones,
                         total_notificaciones=total_notificaciones,
                         recomendaciones=recomendaciones,
                         populares=populares)