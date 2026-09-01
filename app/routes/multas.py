"""
Rutas de Multas - LibroVivo
Gestion de multas por retraso
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.utils.decorators import login_required, bibliotecario_required, admin_required
from app.services.multa_service import pagar_multa, condonar_multa, obtener_resumen_multas_usuario
from app.models.multa import Multa
from app.models.prestamo import Prestamo

multas_bp = Blueprint('multas', __name__)


@multas_bp.route('/')
@bibliotecario_required
def lista():
    """
    Lista de multas (bibliotecario y admin)
    """
    estado = request.args.get('estado', 'pendiente')
    pagina = request.args.get('pagina', 1, type=int)
    
    if estado == 'pendiente':
        multas = Multa.listar_pendientes(pagina=pagina)
    else:
        multas = Multa.listar_todas(estado=estado, pagina=pagina)
    
    # Totales
    total_pendiente = Multa.total_recaudado()  # Esto esta mal, deberia ser total pendiente
    # Corregir:
    sql = "SELECT SUM(monto) as total FROM multas WHERE estado = 'pendiente'"
    from app.database import ejecutar_consulta
    resultado = ejecutar_consulta(sql, fetchone=True)
    total_pendiente = resultado['total'] if resultado and resultado['total'] else 0
    
    return render_template('multas/lista.html',
                         multas=multas,
                         estado=estado,
                         total_pendiente=total_pendiente)


@multas_bp.route('/<int:multa_id>')
@login_required
def ver(multa_id):
    """
    Ver detalle de una multa
    """
    multa = Multa.obtener_por_id(multa_id)
    
    if not multa:
        flash('Multa no encontrada', 'danger')
        return redirect(url_for('multas.lista'))
    
    # Estudiante solo ve sus propias multas
    if session.get('rol') == 'estudiante' and multa['usuario_id'] != session['usuario_id']:
        flash('No puedes ver esta multa', 'danger')
        return redirect(url_for('dashboard.index'))
    
    return render_template('multas/ver.html', multa=multa)


@multas_bp.route('/<int:multa_id>/pagar', methods=['GET', 'POST'])
@bibliotecario_required
def pagar(multa_id):
    """
    Registrar pago de multa
    """
    multa = Multa.obtener_por_id(multa_id)
    
    if not multa:
        flash('Multa no encontrada', 'danger')
        return redirect(url_for('multas.lista'))
    
    if request.method == 'POST':
        observaciones = request.form.get('observaciones', '').strip()
        bibliotecario_id = session['usuario_id']
        
        exito, mensaje = pagar_multa(multa_id, bibliotecario_id, observaciones)
        
        if exito:
            flash(mensaje, 'success')
        else:
            flash(mensaje, 'danger')
        
        return redirect(url_for('multas.lista'))
    
    return render_template('multas/pagar.html', multa=multa)


@multas_bp.route('/<int:multa_id>/condonar', methods=['POST'])
@admin_required
def condonar(multa_id):
    """
    Condonar multa (solo admin)
    """
    observaciones = request.form.get('observaciones', '').strip()
    admin_id = session['usuario_id']
    
    exito, mensaje = condonar_multa(multa_id, admin_id, observaciones)
    
    if exito:
        flash(mensaje, 'success')
    else:
        flash(mensaje, 'danger')
    
    return redirect(url_for('multas.lista'))


@multas_bp.route('/mis-multas')
@login_required
def mis_multas():
    """
    Mis multas (vista de estudiante)
    """
    usuario_id = session['usuario_id']
    multas = Multa.listar_por_usuario(usuario_id)
    resumen = obtener_resumen_multas_usuario(usuario_id)
    
    return render_template('multas/mis_multas.html',
                         multas=multas,
                         resumen=resumen)


@multas_bp.route('/morosos')
@admin_required
def morosos():
    """
    Reporte de morosos (solo admin)
    """
    top_morosos = Multa.top_morosos(50)
    return render_template('multas/morosos.html', morosos=top_morosos)