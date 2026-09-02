"""
Rutas de Prestamos - LibroVivo
Prestamos, devoluciones y renovaciones
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.utils.decorators import login_required, bibliotecario_required, estudiante_required
from app.services.prestamo_service import (
    crear_prestamo, devolver_prestamo, renovar_prestamo,
    extender_prestamo_bibliotecario, validar_horario_biblioteca
)
from app.models.prestamo import Prestamo
from app.models.ejemplar import Ejemplar
from app.models.usuario import Usuario
from app.models.libro import Libro

prestamos_bp = Blueprint('prestamos', __name__)


@prestamos_bp.route('/')
@bibliotecario_required
def lista():
    """
    Lista de prestamos (bibliotecario y admin)
    """
    estado = request.args.get('estado', 'activo')
    pagina = request.args.get('pagina', 1, type=int)
    por_pagina = 10
    
    if estado == 'activo':
        prestamos = Prestamo.listar_activos(pagina=pagina, por_pagina=por_pagina)
    elif estado == 'vencidos':
        prestamos = Prestamo.listar_vencidos()
    else:
        # Todos
        sql = """
            SELECT p.*, l.titulo as libro_titulo,
                   u.nombre as usuario_nombre, u.apellido as usuario_apellido
            FROM prestamos p
            JOIN ejemplares e ON p.ejemplar_id = e.id
            JOIN libros l ON e.libro_id = l.id
            JOIN usuarios u ON p.usuario_id = u.id
            ORDER BY p.fecha_prestamo DESC
            LIMIT %s OFFSET %s
        """
        from app.database import ejecutar_consulta
        prestamos = ejecutar_consulta(sql, (por_pagina, (pagina - 1) * por_pagina), fetchall=True) or []
    
    # Calcular total para paginacion
    total_sql = "SELECT COUNT(*) as total FROM prestamos WHERE 1=1"
    if estado == 'activo':
        total_sql += " AND estado = 'activo'"
    elif estado == 'vencidos':
        total_sql += " AND estado = 'activo' AND fecha_devolucion_prevista < CURDATE()"
    total_result = ejecutar_consulta(total_sql, fetchone=True)
    total_prestamos = total_result['total'] if total_result else 0
    total_paginas = (total_prestamos + por_pagina - 1) // por_pagina
    
    # Resumen (valores por defecto para evitar errores)
    resumen = {
        'activos': 0,
        'devueltos': 0,
        'vencidos': 0,
        'vencen_manana': 0
    }
    
    return render_template('prestamos/lista.html',
                         prestamos=prestamos,
                         estado=estado,
                         estado_filtro=estado,
                         pagina_actual=pagina,
                         total_paginas=total_paginas,
                         resumen=resumen)


@prestamos_bp.route('/nuevo/paso1', methods=['GET', 'POST'])
@bibliotecario_required
def nuevo_paso1():
    """
    Paso 1: Seleccionar estudiante
    """
    # Validar horario
    valido, mensaje = validar_horario_biblioteca()
    if not valido:
        flash(mensaje, 'warning')
    
    if request.method == 'POST':
        usuario_id = request.form.get('usuario_id', type=int)
        
        if not usuario_id:
            flash('Selecciona un estudiante', 'warning')
        else:
            # Verificar que el usuario exista y sea estudiante
            usuario = Usuario.obtener_por_id(usuario_id)
            if not usuario or usuario.rol != 'estudiante':
                flash('Usuario no valido', 'danger')
            else:
                return redirect(url_for('prestamos.nuevo_paso2', usuario_id=usuario_id))
    
    # Buscar estudiantes
    query = request.args.get('q', '').strip()
    if query:
        # Buscar por nombre, apellido o documento
        sql = """
            SELECT id, nombre, apellido, email, documento
            FROM usuarios
            WHERE rol = 'estudiante' AND activo = 1
            AND (nombre LIKE %s OR apellido LIKE %s OR documento LIKE %s OR email LIKE %s)
            ORDER BY nombre
        """
        like = f"%{query}%"
        from app.database import ejecutar_consulta
        estudiantes = ejecutar_consulta(sql, (like, like, like, like), fetchall=True) or []
    else:
        estudiantes = Usuario.listar_todos(rol='estudiante', activo=True, por_pagina=20)
    
    return render_template('prestamos/paso1_seleccionar_estudiante.html',
                         estudiantes=estudiantes,
                         query=query)


@prestamos_bp.route('/nuevo/paso2/<int:usuario_id>', methods=['GET', 'POST'])
@bibliotecario_required
def nuevo_paso2(usuario_id):
    """
    Paso 2: Seleccionar libro y ejemplar
    """
    usuario = Usuario.obtener_por_id(usuario_id)
    
    if not usuario:
        flash('Estudiante no encontrado', 'danger')
        return redirect(url_for('prestamos.nuevo_paso1'))
    
    # Mostrar prestamos activos del estudiante
    prestamos_activos = Prestamo.listar_por_usuario(usuario_id, estado='activo')
    
    if request.method == 'POST':
        ejemplar_id = request.form.get('ejemplar_id', type=int)
        
        if not ejemplar_id:
            flash('Selecciona un ejemplar', 'warning')
        else:
            return redirect(url_for('prestamos.nuevo_paso3',
                                  usuario_id=usuario_id,
                                  ejemplar_id=ejemplar_id))
    
    # Buscar libros disponibles
    query = request.args.get('q', '').strip()
    if query:
        libros = Libro.buscar(query)
        # Filtrar solo los que tienen ejemplares disponibles
        libros_con_ejemplares = []
        for libro in libros:
            ejemplares = Ejemplar.listar_disponibles(libro_id=libro['id'], es_prestable=True)
            if ejemplares:
                libro['ejemplares_disponibles'] = ejemplares
                libros_con_ejemplares.append(libro)
        libros = libros_con_ejemplares
    else:
        # Mostrar libros populares
        libros = Libro.mas_prestados(10)
        for libro in libros:
            ejemplares = Ejemplar.listar_disponibles(libro_id=libro['id'], es_prestable=True)
            libro['ejemplares_disponibles'] = ejemplares
    
    return render_template('prestamos/paso2_seleccionar_libro.html',
                         usuario=usuario,
                         prestamos_activos=prestamos_activos,
                         libros=libros,
                         query=query)


@prestamos_bp.route('/nuevo/paso3', methods=['GET', 'POST'])
@bibliotecario_required
def nuevo_paso3():
    """
    Paso 3: Confirmar prestamo
    """
    usuario_id = request.args.get('usuario_id', type=int)
    ejemplar_id = request.args.get('ejemplar_id', type=int)
    
    if not usuario_id or not ejemplar_id:
        flash('Datos incompletos', 'danger')
        return redirect(url_for('prestamos.nuevo_paso1'))
    
    usuario = Usuario.obtener_por_id(usuario_id)
    ejemplar = Ejemplar.obtener_por_id(ejemplar_id)
    
    if not usuario or not ejemplar:
        flash('Datos no encontrados', 'danger')
        return redirect(url_for('prestamos.nuevo_paso1'))
    
    if request.method == 'POST':
        bibliotecario_id = session['usuario_id']
        
        exito, mensaje, prestamo_id = crear_prestamo(ejemplar_id, usuario_id, bibliotecario_id)
        
        if exito:
            flash(mensaje, 'success')
            return redirect(url_for('prestamos.ver', prestamo_id=prestamo_id))
        else:
            flash(mensaje, 'danger')
            return redirect(url_for('prestamos.nuevo_paso2', usuario_id=usuario_id))
    
    # Calcular fecha de devolucion
    from datetime import datetime, timedelta
    from app.config import Config
    fecha_devolucion = datetime.now() + timedelta(days=Config.DIAS_PRESTAMO)
    
    return render_template('prestamos/paso3_confirmar_prestamo.html',
                         usuario=usuario,
                         ejemplar=ejemplar,
                         fecha_devolucion=fecha_devolucion)


@prestamos_bp.route('/<int:prestamo_id>')
@login_required
def ver(prestamo_id):
    """
    Ver detalle de un prestamo
    """
    prestamo = Prestamo.obtener_por_id(prestamo_id)
    
    if not prestamo:
        flash('Prestamo no encontrado', 'danger')
        return redirect(url_for('prestamos.lista'))
    
    # Validar que el estudiante solo vea sus propios prestamos
    if session.get('rol') == 'estudiante' and prestamo['usuario_id'] != session['usuario_id']:
        flash('No puedes ver este prestamo', 'danger')
        return redirect(url_for('dashboard.index'))
    
    return render_template('prestamos/ver.html', prestamo=prestamo)


@prestamos_bp.route('/<int:prestamo_id>/devolver', methods=['GET', 'POST'])
@bibliotecario_required
def devolver(prestamo_id):
    """
    Registrar devolucion de un prestamo
    """
    prestamo = Prestamo.obtener_por_id(prestamo_id)
    
    if not prestamo:
        flash('Prestamo no encontrado', 'danger')
        return redirect(url_for('prestamos.lista'))
    
    if request.method == 'POST':
        observaciones = request.form.get('observaciones', '').strip()
        bibliotecario_id = session['usuario_id']
        
        exito, mensaje, multa = devolver_prestamo(prestamo_id, bibliotecario_id, observaciones)
        
        if exito:
            if multa:
                flash(f"{mensaje}. Multa generada: ${multa['monto']:,.0f} COP", 'warning')
            else:
                flash(mensaje, 'success')
        else:
            flash(mensaje, 'danger')
        
        return redirect(url_for('prestamos.lista'))
    
    return render_template('prestamos/devolver.html', prestamo=prestamo)


@prestamos_bp.route('/<int:prestamo_id>/renovar', methods=['POST'])
@estudiante_required
def renovar(prestamo_id):
    """
    Renovar prestamo (estudiante)
    """
    usuario_id = session['usuario_id']
    
    exito, mensaje = renovar_prestamo(prestamo_id, usuario_id)
    
    if exito:
        flash(mensaje, 'success')
    else:
        flash(mensaje, 'warning')
    
    return redirect(url_for('dashboard.index'))


@prestamos_bp.route('/<int:prestamo_id>/extender', methods=['POST'])
@bibliotecario_required
def extender(prestamo_id):
    """
    Extender prestamo (bibliotecario)
    """
    dias = request.form.get('dias', 2, type=int)
    bibliotecario_id = session['usuario_id']
    
    exito, mensaje = extender_prestamo_bibliotecario(prestamo_id, bibliotecario_id, dias)
    
    if exito:
        flash(mensaje, 'success')
    else:
        flash(mensaje, 'danger')
    
    return redirect(url_for('prestamos.lista'))


@prestamos_bp.route('/mis-prestamos')
@estudiante_required
def mis_prestamos():
    """
    Mis prestamos (vista de estudiante)
    """
    usuario_id = session['usuario_id']
    prestamos = Prestamo.listar_por_usuario(usuario_id)
    return render_template('prestamos/mis_prestamos.html', prestamos=prestamos)