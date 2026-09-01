"""
Rutas de Reseñas - LibroVivo
Calificaciones y reseñas de libros
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.utils.decorators import login_required, estudiante_required, admin_required
from app.models.resena import Resena
from app.models.libro import Libro

resenas_bp = Blueprint('resenas', __name__)


@resenas_bp.route('/')
@login_required
def lista():
    """
    Lista de resenas
    """
    libro_id = request.args.get('libro_id', type=int)
    
    if libro_id:
        resenas = Resena.listar_por_libro(libro_id, solo_activas=True)
        libro = Libro.obtener_por_id(libro_id)
    else:
        resenas = Resena.listar_todas(solo_activas=True, por_pagina=50)
        libro = None
    
    return render_template('resenas/lista.html',
                         resenas=resenas,
                         libro=libro)


@resenas_bp.route('/crear/<int:libro_id>', methods=['GET', 'POST'])
@estudiante_required
def crear(libro_id):
    """
    Crear resena
    """
    libro = Libro.obtener_por_id(libro_id)
    
    if not libro:
        flash('Libro no encontrado', 'danger')
        return redirect(url_for('libros.catalogo'))
    
    # Verificar que no haya resenado ya
    if Resena.usuario_ha_resenado(libro_id, session['usuario_id']):
        flash('Ya has resenado este libro', 'warning')
        return redirect(url_for('libros.ver', libro_id=libro_id))
    
    if request.method == 'POST':
        calificacion = request.form.get('calificacion', type=int)
        comentario = request.form.get('comentario', '').strip()
        
        # Validaciones
        if not calificacion or calificacion < 1 or calificacion > 5:
            flash('La calificacion debe ser entre 1 y 5 estrellas', 'warning')
            return render_template('resenas/crear.html', libro=libro)
        
        resena_id = Resena.crear(
            libro_id=libro_id,
            usuario_id=session['usuario_id'],
            calificacion=calificacion,
            comentario=comentario or None
        )
        
        if resena_id:
            flash('Resena publicada exitosamente', 'success')
            return redirect(url_for('libros.ver', libro_id=libro_id))
        else:
            flash('Error al publicar la resena', 'danger')
    
    return render_template('resenas/crear.html', libro=libro)


@resenas_bp.route('/<int:resena_id>/editar', methods=['GET', 'POST'])
@estudiante_required
def editar(resena_id):
    """
    Editar resena
    """
    resena = Resena.obtener_por_id(resena_id)
    
    if not resena:
        flash('Resena no encontrada', 'danger')
        return redirect(url_for('dashboard.index'))
    
    # Solo el autor puede editar
    if resena['usuario_id'] != session['usuario_id'] and session.get('rol') != 'admin':
        flash('No puedes editar esta resena', 'danger')
        return redirect(url_for('dashboard.index'))
    
    if request.method == 'POST':
        calificacion = request.form.get('calificacion', type=int)
        comentario = request.form.get('comentario', '').strip()
        
        if Resena.actualizar(resena_id, calificacion=calificacion, comentario=comentario):
            flash('Resena actualizada', 'success')
            return redirect(url_for('libros.ver', libro_id=resena['libro_id']))
        else:
            flash('Error al actualizar', 'danger')
    
    return render_template('resenas/editar.html', resena=resena)


@resenas_bp.route('/<int:resena_id>/eliminar', methods=['POST'])
@admin_required
def eliminar(resena_id):
    """
    Eliminar resena (moderacion - solo admin)
    """
    resena = Resena.obtener_por_id(resena_id)
    
    if not resena:
        flash('Resena no encontrada', 'danger')
        return redirect(url_for('resenas.lista'))
    
    if Resena.eliminar(resena_id):
        flash('Resena eliminada exitosamente', 'success')
    else:
        flash('Error al eliminar la resena', 'danger')
    
    return redirect(url_for('resenas.lista'))


@resenas_bp.route('/<int:resena_id>/restaurar', methods=['POST'])
@admin_required
def restaurar(resena_id):
    """
    Restaurar resena eliminada
    """
    if Resena.restaurar(resena_id):
        flash('Resena restaurada', 'success')
    else:
        flash('Error al restaurar', 'danger')
    
    return redirect(url_for('resenas.lista'))


@resenas_bp.route('/moderar')
@admin_required
def moderar():
    """
    Panel de moderacion de resenas
    """
    # Resenas activas
    resenas_activas = Resena.listar_todas(solo_activas=True, por_pagina=100)
    
    # Resenas eliminadas
    resenas_eliminadas = Resena.listar_todas(solo_activas=False, por_pagina=100)
    
    return render_template('resenas/moderar.html',
                         resenas_activas=resenas_activas,
                         resenas_eliminadas=resenas_eliminadas)