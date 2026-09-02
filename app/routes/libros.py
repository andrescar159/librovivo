"""
Rutas de Libros - LibroVivo
CRUD de libros, catalogo y busqueda
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app.utils.decorators import login_required, bibliotecario_required
from app.models.libro import Libro
from app.models.ejemplar import Ejemplar
from app.models.categoria_dewey import CategoriaDewey
from app.models.resena import Resena
from app.utils.helpers import guardar_archivo, truncar_texto

libros_bp = Blueprint('libros', __name__)


@libros_bp.route('/catalogo')
@login_required
def catalogo():
    """
    Catalogo de libros para todos los usuarios
    """
    # Filtros
    categoria_id = request.args.get('categoria', type=int)
    query = request.args.get('q', '').strip()
    pagina = request.args.get('pagina', 1, type=int)
    por_pagina = 12  # Libros por página
    
    categorias = CategoriaDewey.listar_todas()
    
    if query:
        libros = Libro.buscar(query, categoria_id=categoria_id)
        # Búsqueda no tiene paginación en el modelo, así que mostramos todos
        total_paginas = 1
        pagina_actual = 1
    else:
        # Calcular total para paginación
        total_libros = Libro.contar(activo=True, categoria_id=categoria_id)
        total_paginas = (total_libros + por_pagina - 1) // por_pagina
        pagina_actual = pagina
        
        libros = Libro.listar_todos(activo=True, categoria_id=categoria_id, pagina=pagina, por_pagina=por_pagina)
    
    return render_template('libros/catalogo.html',
                         libros=libros,
                         categorias=categorias,
                         query=query,
                         categoria_seleccionada=categoria_id,
                         pagina_actual=pagina_actual,
                         total_paginas=total_paginas)


@libros_bp.route('/buscar', methods=['GET', 'POST'])
@login_required
def buscar():
    """
    Busqueda avanzada de libros
    """
    if request.method == 'POST':
        query = request.form.get('query', '').strip()
        categoria_id = request.form.get('categoria', type=int)
        
        if not query and not categoria_id:
            flash('Ingresa un termino de busqueda o selecciona una categoria', 'warning')
            return redirect(url_for('libros.catalogo'))
        
        libros = Libro.buscar(query, categoria_id=categoria_id)
        categorias = CategoriaDewey.listar_todas()
        
        return render_template('libros/resultados_busqueda.html',
                             libros=libros,
                             query=query,
                             categorias=categorias,
                             categoria_seleccionada=categoria_id)
    
    return redirect(url_for('libros.catalogo'))


@libros_bp.route('/<int:libro_id>')
@login_required
def ver(libro_id):
    """
    Ver detalle de un libro
    """
    libro = Libro.obtener_por_id(libro_id)
    
    if not libro:
        flash('Libro no encontrado', 'danger')
        return redirect(url_for('libros.catalogo'))
    
    # Ejemplares
    ejemplares = Ejemplar.listar_por_libro(libro_id, activo=True)
    
    # Resenas
    resenas = Resena.listar_por_libro(libro_id, solo_activas=True)
    promedio = Resena.obtener_promedio_libro(libro_id)
    
    # Verificar si el usuario ya reseno
    ya_reseno = False
    if session.get('rol') in ['estudiante', 'admin']:
        ya_reseno = Resena.usuario_ha_resenado(libro_id, session['usuario_id'])
    
    # Verificar si tiene reserva activa
    from app.models.reserva import Reserva
    tiene_reserva = Reserva.usuario_tiene_reserva_activa(libro_id, session['usuario_id'])
    
    return render_template('libros/ver.html',
                         libro=libro,
                         ejemplares=ejemplares,
                         resenas=resenas,
                         promedio=promedio,
                         ya_reseno=ya_reseno,
                         tiene_reserva=tiene_reserva)


@libros_bp.route('/crear', methods=['GET', 'POST'])
@bibliotecario_required
def crear():
    """
    Crear nuevo libro (admin y bibliotecario)
    """
    if request.method == 'POST':
        isbn = request.form.get('isbn', '').strip()
        titulo = request.form.get('titulo', '').strip()
        editorial = request.form.get('editorial', '').strip()
        anio = request.form.get('anio_publicacion', type=int)
        categoria_id = request.form.get('categoria_id', type=int)
        descripcion = request.form.get('descripcion', '').strip()
        area_conocimiento = request.form.get('area_conocimiento', '').strip()
        
        # Validaciones
        if not titulo or not categoria_id:
            flash('Titulo y categoria son obligatorios', 'warning')
            categorias = CategoriaDewey.listar_todas()
            return render_template('libros/crear.html', categorias=categorias)
        
        # Verificar ISBN unico si se proporciono
        if isbn:
            existente = Libro.obtener_por_isbn(isbn)
            if existente:
                flash('Ya existe un libro con este ISBN', 'warning')
                categorias = CategoriaDewey.listar_todas()
                return render_template('libros/crear.html', categorias=categorias)
        
        # Procesar portada
        portada_url = None
        if 'portada' in request.files:
            archivo = request.files['portada']
            if archivo.filename:
                portada_url = guardar_archivo(archivo, 'portadas')
        
        # Crear libro
        libro_id = Libro.crear(
            categoria_id=categoria_id,
            isbn=isbn or None,
            titulo=titulo,
            editorial=editorial or None,
            anio_publicacion=anio,
            descripcion=descripcion or None,
            portada_url=portada_url,
            area_conocimiento=area_conocimiento or None
        )
        
        if libro_id:
            # Procesar autores
            autores_input = request.form.get('autores', '').strip()
            if autores_input:
                from app.models.autor import Autor
                nombres_autores = [a.strip() for a in autores_input.split(',') if a.strip()]
                for nombre_autor in nombres_autores:
                    # Buscar o crear autor
                    autor = Autor.obtener_por_nombre(nombre_autor)
                    if not autor:
                        autor_id = Autor.crear(nombre_autor)
                    else:
                        autor_id = autor['id']
                    
                    Libro.agregar_autor(libro_id, autor_id)
            
            flash('Libro creado exitosamente', 'success')
            return redirect(url_for('libros.ver', libro_id=libro_id))
        else:
            flash('Error al crear el libro', 'danger')
    
    categorias = CategoriaDewey.listar_todas()
    return render_template('libros/crear.html', categorias=categorias)


@libros_bp.route('/<int:libro_id>/editar', methods=['GET', 'POST'])
@bibliotecario_required
def editar(libro_id):
    """
    Editar libro
    """
    libro = Libro.obtener_por_id(libro_id)
    
    if not libro:
        flash('Libro no encontrado', 'danger')
        return redirect(url_for('libros.catalogo'))
    
    if request.method == 'POST':
        datos = {
            'titulo': request.form.get('titulo', '').strip(),
            'editorial': request.form.get('editorial', '').strip() or None,
            'anio_publicacion': request.form.get('anio_publicacion', type=int),
            'descripcion': request.form.get('descripcion', '').strip() or None,
            'area_conocimiento': request.form.get('area_conocimiento', '').strip() or None,
            'activo': 1 if request.form.get('activo') == 'on' else 0
        }
        
        # Procesar portada
        if 'portada' in request.files:
            archivo = request.files['portada']
            if archivo.filename:
                # Eliminar portada anterior
                if libro.get('portada_url'):
                    from app.utils.helpers import eliminar_archivo
                    eliminar_archivo(libro['portada_url'])
                
                datos['portada_url'] = guardar_archivo(archivo, 'portadas')
        
        if Libro.actualizar(libro_id, **datos):
            flash('Libro actualizado exitosamente', 'success')
            return redirect(url_for('libros.ver', libro_id=libro_id))
        else:
            flash('Error al actualizar el libro', 'danger')
    
    categorias = CategoriaDewey.listar_todas()
    autores = Libro.obtener_autores(libro_id)
    return render_template('libros/editar.html',
                         libro=libro,
                         categorias=categorias,
                         autores=autores)


@libros_bp.route('/<int:libro_id>/ejemplares', methods=['GET', 'POST'])
@bibliotecario_required
def gestionar_ejemplares(libro_id):
    """
    Gestionar ejemplares de un libro
    """
    libro = Libro.obtener_por_id(libro_id)
    
    if not libro:
        flash('Libro no encontrado', 'danger')
        return redirect(url_for('libros.catalogo'))
    
    if request.method == 'POST':
        accion = request.form.get('accion')
        
        if accion == 'crear':
            codigo_barras = request.form.get('codigo_barras', '').strip()
            es_prestable = request.form.get('es_prestable') == 'on'
            ubicacion = request.form.get('ubicacion', '').strip()
            
            if not codigo_barras:
                # Generar codigo automatico
                from app.utils.helpers import generar_codigo_barras
                codigo_barras = generar_codigo_barras()
            
            # Verificar que no exista
            existente = Ejemplar.obtener_por_codigo(codigo_barras)
            if existente:
                flash('Ya existe un ejemplar con este codigo', 'warning')
            else:
                Ejemplar.crear(libro_id, codigo_barras, es_prestable, ubicacion or None)
                flash('Ejemplar creado exitosamente', 'success')
        
        elif accion == 'editar':
            ejemplar_id = request.form.get('ejemplar_id', type=int)
            estado = request.form.get('estado')
            es_prestable = request.form.get('es_prestable') == 'on'
            ubicacion = request.form.get('ubicacion', '').strip()
            
            Ejemplar.actualizar(ejemplar_id, estado=estado, es_prestable=es_prestable,
                               ubicacion=ubicacion or None)
            flash('Ejemplar actualizado', 'success')
        
        elif accion == 'eliminar':
            ejemplar_id = request.form.get('ejemplar_id', type=int)
            Ejemplar.eliminar(ejemplar_id)
            flash('Ejemplar eliminado', 'success')
    
    ejemplares = Ejemplar.listar_por_libro(libro_id, activo=True)
    return render_template('libros/ejemplares.html', libro=libro, ejemplares=ejemplares)