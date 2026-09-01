"""
Rutas de Reportes - LibroVivo
Generacion de reportes en PDF
"""
from flask import Blueprint, render_template, request, send_file, flash, redirect, url_for
from app.utils.decorators import admin_required
from app.services.reporte_service import (
    generar_reporte_prestamos,
    generar_reporte_morosos,
    generar_reporte_inventario
)
from app.models.prestamo import Prestamo
from app.models.multa import Multa
from app.models.libro import Libro
from app.models.usuario import Usuario
from io import BytesIO
from datetime import datetime

reportes_bp = Blueprint('reportes', __name__)


@reportes_bp.route('/')
@admin_required
def index():
    """
    Panel de reportes
    """
    # Estadisticas para los filtros
    total_libros = Libro.contar(activo=True)
    total_usuarios = Usuario.contar(activo=True)
    total_prestamos_activos = len(Prestamo.listar_activos(por_pagina=1000))
    total_multas_pendientes = len(Multa.listar_pendientes(por_pagina=1000))
    
    return render_template('reportes/index.html',
                         total_libros=total_libros,
                         total_usuarios=total_usuarios,
                         total_prestamos_activos=total_prestamos_activos,
                         total_multas_pendientes=total_multas_pendientes)


@reportes_bp.route('/prestamos', methods=['GET', 'POST'])
@admin_required
def reporte_prestamos():
    """
    Reporte de prestamos
    """
    if request.method == 'POST':
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')
        formato = request.form.get('formato', 'pdf')
        
        # Convertir fechas
        if fecha_inicio:
            fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d')
        if fecha_fin:
            fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d')
        
        # Generar reporte
        contenido = generar_reporte_prestamos(fecha_inicio, fecha_fin, formato)
        
        if contenido:
            if formato == 'pdf':
                return send_file(
                    BytesIO(contenido),
                    mimetype='application/pdf',
                    as_attachment=True,
                    download_name=f'reporte_prestamos_{datetime.now().strftime("%Y%m%d")}.pdf'
                )
            else:
                return render_template('reportes/ver_reporte.html',
                                     contenido=contenido.decode('utf-8'),
                                     titulo='Reporte de Prestamos')
        else:
            flash('Error al generar el reporte', 'danger')
    
    return render_template('reportes/seleccionar_filtros.html',
                         tipo='prestamos',
                         titulo='Reporte de Prestamos')


@reportes_bp.route('/morosos')
@admin_required
def reporte_morosos():
    """
    Reporte de morosos
    """
    contenido = generar_reporte_morosos()
    
    if contenido:
        return send_file(
            BytesIO(contenido),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'reporte_morosos_{datetime.now().strftime("%Y%m%d")}.pdf'
        )
    else:
        flash('Error al generar el reporte', 'danger')
        return redirect(url_for('reportes.index'))


@reportes_bp.route('/inventario')
@admin_required
def reporte_inventario():
    """
    Reporte de inventario
    """
    contenido = generar_reporte_inventario()
    
    if contenido:
        return send_file(
            BytesIO(contenido),
            mimetype='application/pdf',
            as_attachment=True,
            download_name=f'reporte_inventario_{datetime.now().strftime("%Y%m%d")}.pdf'
        )
    else:
        flash('Error al generar el reporte', 'danger')
        return redirect(url_for('reportes.index'))


@reportes_bp.route('/estadisticas')
@admin_required
def estadisticas():
    """
    Estadisticas generales
    """
    from datetime import datetime
    
    anio_actual = datetime.now().year
    
    # Prestamos por mes
    prestamos_mensuales = Prestamo.estadisticas_mensuales(anio_actual)
    
    # Libros mas prestados
    libros_populares = Libro.mas_prestados(10)
    
    # Top morosos
    top_morosos = Multa.top_morosos(10)
    
    # Total recaudado
    total_recaudado = Multa.total_recaudado()
    
    return render_template('reportes/estadisticas.html',
                         prestamos_mensuales=prestamos_mensuales,
                         libros_populares=libros_populares,
                         top_morosos=top_morosos,
                         total_recaudado=total_recaudado,
                         anio=anio_actual)