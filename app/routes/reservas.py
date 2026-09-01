"""
Rutas de Reservas - LibroVivo
Reservas de libros
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.utils.decorators import login_required, estudiante_required, bibliotecario_required
from app.services.reserva_service import (
    crear_reserva, cancelar_reserva, completar_reserva,
    procesar_reservas_vencidas, notificar_reservas_disponibles
)
from app.models.reserva import Reserva
from app.models.libro import Libro

reservas_bp = Blueprint('reservas', __name__)


@reservas_bp.route('/')
@bibliotecario_required
def lista():
    """
    Lista de reservas (bibliotecario y admin)
    """
    estado = request.args.get('estado', 'activa')
    
    if estado == 'activa':
        reservas = Reserva.listar_activas()
    elif estado == 'vencidas':
        reservas = Reserva.listar_vencidas()
    else:
        reservas = Reserva.listar_activas()  # Por defecto activas
    
    return render_template('reservas/lista.html',
                         reservas=reservas,
                         estado=estado)


@reservas_bp.route('/nueva/<int:libro_id>', methods=['POST'])
@estudiante_required
def crear(libro_id):
    """
    Crear nueva reserva
    """
    usuario_id = session['usuario_id']
    
    exito, mensaje, reserva_id = crear_reserva(libro_id, usuario_id)
    
    if exito:
        flash(mensaje, 'success')
    else:
        flash(mensaje, 'warning')
    
    return redirect(url_for('libros.ver', libro_id=libro_id))


@reservas_bp.route('/<int:reserva_id>/cancelar', methods=['POST'])
@estudiante_required
def cancelar(reserva_id):
    """
    Cancelar reserva
    """
    usuario_id = session['usuario_id']
    
    exito, mensaje = cancelar_reserva(reserva_id, usuario_id)
    
    if exito:
        flash(mensaje, 'success')
    else:
        flash(mensaje, 'warning')
    
    return redirect(url_for('dashboard.index'))


@reservas_bp.route('/<int:reserva_id>/completar', methods=['POST'])
@bibliotecario_required
def completar(reserva_id):
    """
    Completar reserva (cuando el usuario retira el libro)
    """
    exito, mensaje = completar_reserva(reserva_id)
    
    if exito:
        flash(mensaje, 'success')
    else:
        flash(mensaje, 'danger')
    
    return redirect(url_for('reservas.lista'))


@reservas_bp.route('/mis-reservas')
@login_required
def mis_reservas():
    """
    Mis reservas
    """
    usuario_id = session['usuario_id']
    reservas = Reserva.listar_por_usuario(usuario_id)
    return render_template('reservas/mis_reservas.html', reservas=reservas)


@reservas_bp.route('/procesar-vencidas')
@bibliotecario_required
def procesar_vencidas():
    """
    Procesar reservas vencidas (ejecutar manualmente)
    """
    cantidad = procesar_reservas_vencidas()
    flash(f'{cantidad} reservas marcadas como vencidas', 'info')
    return redirect(url_for('reservas.lista'))


@reservas_bp.route('/notificar-disponibles')
@bibliotecario_required
def notificar_disponibles():
    """
    Notificar reservas disponibles (ejecutar manualmente)
    """
    notificaciones = notificar_reservas_disponibles()
    flash(f'{len(notificaciones)} notificaciones enviadas', 'info')
    return redirect(url_for('reservas.lista'))