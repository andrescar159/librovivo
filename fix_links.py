#!/usr/bin/env python3
"""
fix_links.py - Corrección masiva de enlaces rotos en LibroVivo
Ejecutar desde la raíz del proyecto: python fix_links.py
"""
import os
import re
import shutil
from pathlib import Path

BASE_DIR = Path(__file__).parent
TEMPLATES_DIR = BASE_DIR / "app" / "templates"
ROUTES_DIR = BASE_DIR / "app" / "routes"

backups = []
changes = []

def backup_and_replace(filepath, replacements, file_desc):
    """Aplica reemplazos regex a un archivo con backup"""
    global changes, backups
    content = filepath.read_text(encoding='utf-8')
    original = content
    made = []
    
    for pattern, repl, desc in replacements:
        new_content, count = re.subn(pattern, repl, content)
        if count > 0:
            made.append(f"  {desc}: {count} vez/veces")
            content = new_content
    
    if made:
        # Backup
        bak = filepath.with_suffix(filepath.suffix + '.bak')
        shutil.copy2(filepath, bak)
        backups.append(str(bak))
        filepath.write_text(content, encoding='utf-8')
        changes.append(f"[{file_desc}] {filepath.name}\n" + "\n".join(made))
        return True
    return False

# ============================================================
# 1. CORRECCIONES EN TEMPLATES
# ============================================================

template_fixes = {
    # libros/catalogo.html
    "libros/catalogo.html": [
        (r"url_for\('libros\.ver',\s*id=libro\.id\)", r"url_for('libros.ver', libro_id=libro.id)", "libros.ver id→libro_id"),
    ],
    # libros/editar.html
    "libros/editar.html": [
        (r"url_for\('libros\.ver',\s*id=libro\.id\)", r"url_for('libros.ver', libro_id=libro.id)", "libros.ver id→libro_id"),
        (r"url_for\('libros\.editar',\s*id=libro\.id\)", r"url_for('libros.editar', libro_id=libro.id)", "libros.editar id→libro_id"),
        (r"url_for\('libros\.agregar_ejemplar'", r"url_for('libros.gestionar_ejemplares'", "agregar_ejemplar→gestionar_ejemplares"),
        (r"url_for\('libros\.editar_ejemplar',\s*id=ej\.id\)", r"url_for('libros.gestionar_ejemplares', libro_id=libro.id)", "editar_ejemplar→gestionar_ejemplares"),
    ],
    # libros/resultados_busqueda.html
    "libros/resultados_busqueda.html": [
        (r"url_for\('libros\.ver',\s*id=libro\.id\)", r"url_for('libros.ver', libro_id=libro.id)", "libros.ver id→libro_id"),
        (r"url_for\('libros\.editar',\s*id=libro\.id\)", r"url_for('libros.editar', libro_id=libro.id)", "libros.editar id→libro_id"),
    ],
    # libros/ver.html
    "libros/ver.html": [
        (r"url_for\('libros\.editar',\s*id=libro\.id\)", r"url_for('libros.editar', libro_id=libro.id)", "libros.editar id→libro_id"),
    ],
    # multas/lista.html
    "multas/lista.html": [
        (r"url_for\('multas\.pagar',\s*id=m\.id\)", r"url_for('multas.pagar', multa_id=m.id)", "multas.pagar id→multa_id"),
        (r"url_for\('multas\.ver',\s*id=m\.id\)", r"url_for('multas.ver', multa_id=m.id)", "multas.ver id→multa_id"),
        (r"m\.nombre_estudiante", r"m.usuario_nombre", "nombre_estudiante→usuario_nombre"),
        (r"m\.documento_estudiante", r"m.documento|default('')", "documento_estudiante→documento"),
        (r"m\.titulo_libro", r"m.libro_titulo", "titulo_libro→libro_titulo"),
    ],
    # multas/ver.html
    "multas/ver.html": [
        (r"url_for\('multas\.pagar',\s*id=multa\.id\)", r"url_for('multas.pagar', multa_id=multa.id)", "multas.pagar id→multa_id"),
        (r"url_for\('multas\.ver',\s*id=multa\.id\)", r"url_for('multas.ver', multa_id=multa.id)", "multas.ver id→multa_id"),
        (r"multa\.nombre_estudiante", r"multa.usuario_nombre", "nombre_estudiante→usuario_nombre"),
        (r"multa\.documento_estudiante", r"multa.documento|default('')", "documento_estudiante→documento"),
        (r"multa\.titulo_libro", r"multa.libro_titulo", "titulo_libro→libro_titulo"),
    ],
    # multas/mis_multas.html
    "multas/mis_multas.html": [
        (r"url_for\('multas\.ver',\s*id=m\.id\)", r"url_for('multas.ver', multa_id=m.id)", "multas.ver id→multa_id"),
    ],
    # multas/pagar.html
    "multas/pagar.html": [
        (r"url_for\('multas\.procesar_pago'", r"url_for('multas.pagar'", "procesar_pago→pagar"),
    ],
    # prestamos/lista.html
    "prestamos/lista.html": [
        (r"url_for\('prestamos\.devolver',\s*id=p\.id\)", r"url_for('prestamos.devolver', prestamo_id=p.id)", "devolver id→prestamo_id"),
        (r"url_for\('multas\.pagar',\s*prestamo_id=p\.id\)", r"url_for('multas.pagar', multa_id=p.multa_id)", "multas.pagar prestamo_id→multa_id"),
        (r"url_for\('prestamos\.ver',\s*id=p\.id\)", r"url_for('prestamos.ver', prestamo_id=p.id)", "ver id→prestamo_id"),
        (r"p\.nombre_estudiante", r"p.usuario_nombre", "nombre_estudiante→usuario_nombre"),
        (r"p\.documento_estudiante", r"p.documento|default('')", "documento_estudiante→documento"),
        (r"p\.titulo_libro", r"p.libro_titulo", "titulo_libro→libro_titulo"),
        (r"p\.codigo_barras", r"p.codigo_barras|default('')", "codigo_barras con default"),
        (r"estado_filtro", r"estado", "estado_filtro→estado"),
    ],
    # prestamos/ver.html
    "prestamos/ver.html": [
        (r"url_for\('prestamos\.devolver',\s*id=prestamo\.id\)", r"url_for('prestamos.devolver', prestamo_id=prestamo.id)", "devolver id→prestamo_id"),
        (r"url_for\('prestamos\.ver',\s*id=prestamo\.id\)", r"url_for('prestamos.ver', prestamo_id=prestamo.id)", "ver id→prestamo_id"),
        (r"url_for\('prestamos\.renovar',\s*id=prestamo\.id\)", r"url_for('prestamos.renovar', prestamo_id=prestamo.id)", "renovar id→prestamo_id"),
        (r"prestamo\.nombre_estudiante", r"prestamo.usuario_nombre", "nombre_estudiante→usuario_nombre"),
        (r"prestamo\.documento_estudiante", r"prestamo.documento|default('')", "documento_estudiante→documento"),
        (r"prestamo\.titulo_libro", r"prestamo.libro_titulo", "titulo_libro→libro_titulo"),
    ],
    # prestamos/mis_prestamos.html
    "prestamos/mis_prestamos.html": [
        (r"url_for\('prestamos\.ver',\s*id=p\.id\)", r"url_for('prestamos.ver', prestamo_id=p.id)", "ver id→prestamo_id"),
        (r"url_for\('prestamos\.renovar',\s*id=p\.id\)", r"url_for('prestamos.renovar', prestamo_id=p.id)", "renovar id→prestamo_id"),
        (r"p\.titulo_libro", r"p.libro_titulo", "titulo_libro→libro_titulo"),
    ],
    # prestamos/paso1_seleccionar_estudiante.html
    "prestamos/paso1_seleccionar_estudiante.html": [
        (r"url_for\('prestamos\.nuevo_paso2',\s*estudiante_id=e\.id\)", r"url_for('prestamos.nuevo_paso2', usuario_id=e.id)", "estudiante_id→usuario_id"),
        (r"e\.prestamos_activos", r"e.prestamos_activos|default(0)", "prestamos_activos con default"),
        (r"e\.multas_pendientes", r"e.multas_pendientes|default(0)", "multas_pendientes con default"),
    ],
    # prestamos/paso2_seleccionar_libro.html
    "prestamos/paso2_seleccionar_libro.html": [
        (r"url_for\('prestamos\.nuevo_paso3',\s*estudiante_id=usuario_id", r"url_for('prestamos.nuevo_paso3', usuario_id=usuario_id", "estudiante_id→usuario_id"),
    ],
    # prestamos/paso3_confirmar_prestamo.html
    "prestamos/paso3_confirmar_prestamo.html": [
        (r"url_for\('prestamos\.guardar'\)", r"url_for('prestamos.nuevo_paso3')", "guardar→nuevo_paso3"),
    ],
    # prestamos/devolver.html
    "prestamos/devolver.html": [
        (r"url_for\('prestamos\.procesar_devolucion'", r"url_for('prestamos.devolver'", "procesar_devolucion→devolver"),
    ],
    # prestamos/renovar.html
    "prestamos/renovar.html": [
        (r"url_for\('prestamos\.confirmar_renovacion'", r"url_for('prestamos.renovar'", "confirmar_renovacion→renovar"),
    ],
    # reservas/lista.html
    "reservas/lista.html": [
        (r"url_for\('prestamos\.nuevo_paso2',\s*estudiante_id=r\.usuario_id", r"url_for('prestamos.nuevo_paso2', usuario_id=r.usuario_id", "estudiante_id→usuario_id"),
        (r"url_for\('reservas\.notificar',\s*id=r\.id\)", r"url_for('reservas.notificar', reserva_id=r.id)", "notificar id→reserva_id"),
        (r"url_for\('reservas\.cancelar',\s*id=r\.id\)", r"url_for('reservas.cancelar', reserva_id=r.id)", "cancelar id→reserva_id"),
        (r"url_for\('reservas\.ver',\s*id=r\.id\)", r"url_for('reservas.ver', reserva_id=r.id)", "ver id→reserva_id"),
        (r"r\.nombre_estudiante", r"r.usuario_nombre", "nombre_estudiante→usuario_nombre"),
        (r"r\.documento_estudiante", r"r.documento|default('')", "documento_estudiante→documento"),
        (r"r\.titulo_libro", r"r.libro_titulo", "titulo_libro→libro_titulo"),
        (r"r\.autor_libro", r"r.autor_libro|default('')", "autor_libro con default"),
        (r"r\.libro_disponible", r"r.ejemplares_disponibles > 0", "libro_disponible→ejemplares_disponibles"),
        (r"estado_filtro", r"estado", "estado_filtro→estado"),
    ],
    # reservas/mis_reservas.html
    "reservas/mis_reservas.html": [
        (r"url_for\('libros\.ver',\s*id=r\.libro_id\)", r"url_for('libros.ver', libro_id=r.libro_id)", "libros.ver id→libro_id"),
        (r"url_for\('prestamos\.nuevo_paso3',\s*estudiante_id=session\.usuario_id", r"url_for('prestamos.nuevo_paso3', usuario_id=session.usuario_id", "estudiante_id→usuario_id"),
        (r"url_for\('reservas\.cancelar',\s*id=r\.id\)", r"url_for('reservas.cancelar', reserva_id=r.id)", "cancelar id→reserva_id"),
        (r"r\.titulo_libro", r"r.libro_titulo", "titulo_libro→libro_titulo"),
        (r"r\.autor_libro", r"r.autor_libro|default('')", "autor_libro con default"),
        (r"r\.categoria_nombre", r"r.categoria_nombre|default('')", "categoria_nombre con default"),
        (r"r\.libro_disponible", r"r.ejemplares_disponibles > 0", "libro_disponible→ejemplares_disponibles"),
    ],
    # reservas/crear.html
    "reservas/crear.html": [
        (r"url_for\('reservas\.guardar'\)", r"url_for('reservas.crear', libro_id=libro.id)", "guardar→crear"),
    ],
    # resenas/lista.html
    "resenas/lista.html": [
        (r"url_for\('resenas\.editar',\s*id=r\.id\)", r"url_for('resenas.editar', resena_id=r.id)", "editar id→resena_id"),
        (r"url_for\('resenas\.eliminar',\s*id=r\.id\)", r"url_for('resenas.eliminar', resena_id=r.id)", "eliminar id→resena_id"),
    ],
    # resenas/moderar.html
    "resenas/moderar.html": [
        (r"url_for\('resenas\.eliminar',\s*id=r\.id\)", r"url_for('resenas.eliminar', resena_id=r.id)", "eliminar id→resena_id"),
        (r"url_for\('resenas\.restaurar',\s*id=r\.id\)", r"url_for('resenas.restaurar', resena_id=r.id)", "restaurar id→resena_id"),
        (r"url_for\('resenas\.procesar_moderacion'", r"url_for('resenas.eliminar'", "procesar_moderacion→eliminar"),
    ],
    # usuarios/ver.html
    "usuarios/ver.html": [
        (r"url_for\('usuarios\.editar',\s*id=usuario\.id\)", r"url_for('usuarios.editar', usuario_id=usuario.id)", "editar id→usuario_id"),
        (r"url_for\('usuarios\.ver',\s*id=usuario\.id\)", r"url_for('usuarios.ver', usuario_id=usuario.id)", "ver id→usuario_id"),
        (r"p\.titulo_libro", r"p.libro_titulo", "titulo_libro→libro_titulo"),
        (r"r\.titulo_libro", r"r.libro_titulo", "titulo_libro→libro_titulo"),
        (r"resumen\.prestamos_activos", r"resumen.prestamos_activos|default(0)", "resumen con default"),
        (r"resumen\.reservas_activas", r"resumen.reservas_activas|default(0)", "resumen con default"),
        (r"resumen\.multas_pendientes", r"resumen.multas_pendientes|default(0)", "resumen con default"),
    ],
    # usuarios/editar.html
    "usuarios/editar.html": [
        (r"url_for\('usuarios\.editar',\s*id=usuario\.id\)", r"url_for('usuarios.editar', usuario_id=usuario.id)", "editar id→usuario_id"),
        (r"url_for\('usuarios\.ver',\s*id=usuario\.id\)", r"url_for('usuarios.ver', usuario_id=usuario.id)", "ver id→usuario_id"),
    ],
    # usuarios/perfil.html
    "usuarios/perfil.html": [
        (r"url_for\('usuarios\.actualizar_foto'\)", r"url_for('usuarios.editar', usuario_id=session.usuario_id)", "actualizar_foto→editar"),
        (r"url_for\('usuarios\.actualizar_perfil'\)", r"url_for('usuarios.editar', usuario_id=session.usuario_id)", "actualizar_perfil→editar"),
        (r"url_for\('usuarios\.cambiar_password'\)", r"url_for('auth.cambiar_password')", "usuarios.cambiar_password→auth.cambiar_password"),
    ],
    # dashboard/admin.html
    "dashboard/admin.html": [
        (r"url_for\('multas\.ver',\s*multa_id=multa\.id\)", r"url_for('multas.ver', multa_id=multa.id)", "multas.ver (ya correcto, verificar)"),
    ],
}

# ============================================================
# 2. CORRECCIONES EN RUTAS (routes/*.py)
# ============================================================

route_fixes = {
    # libros.py - catalogo necesita paginacion
    "libros.py": [
        (r"return render_template\('libros/catalogo.html',\s*libros=libros,\s*categorias=categorias,\s*query=query,\s*categoria_seleccionada=categoria_id\)",
         r"""# Calcular paginacion
    total_libros = Libro.contar(activo=True, categoria_id=categoria_id)
    total_paginas = (total_libros + por_pagina - 1) // por_pagina if not query else 1
    pagina_actual = pagina
    
    return render_template('libros/catalogo.html',
                         libros=libros,
                         categorias=categorias,
                         query=query,
                         categoria_seleccionada=categoria_id,
                         pagina_actual=pagina_actual,
                         total_paginas=total_paginas)""",
         "Agregar paginacion a catalogo"),
    ],
}

# ============================================================
# EJECUCIÓN
# ============================================================

print("=" * 60)
print("FIX LINKS - LibroVivo")
print("=" * 60)

# Aplicar fixes de templates
for rel_path, replacements in template_fixes.items():
    filepath = TEMPLATES_DIR / rel_path
    if filepath.exists():
        if backup_and_replace(filepath, replacements, rel_path):
            print(f"✅ Corregido: {rel_path}")
    else:
        print(f"⚠️  No encontrado: {rel_path}")

# Aplicar fixes de rutas
for fname, replacements in route_fixes.items():
    filepath = ROUTES_DIR / fname
    if filepath.exists():
        if backup_and_replace(filepath, replacements, fname):
            print(f"✅ Corregido: app/routes/{fname}")
    else:
        print(f"⚠️  No encontrado: app/routes/{fname}")

# Reporte final
print("\n" + "=" * 60)
print("RESUMEN")
print("=" * 60)
if changes:
    print(f"\n✅ Archivos modificados: {len(changes)}")
    for c in changes:
        print(f"\n{c}")
else:
    print("\n⚠️  No se hicieron cambios (¿ya están corregidos?)")

if backups:
    print(f"\n📁 Backups creados ({len(backups)}):")
    for b in backups:
        print(f"   {b}")
    print("\n💡 Si algo falla, restaura con:")
    for b in backups:
        orig = b.replace('.bak', '')
        print(f"   mv {b} {orig}")

print("\n" + "=" * 60)
print("NOTAS:")
print("  1. Revisa los archivos .bak antes de borrarlos")
print("  2. Algunas rutas faltantes (reportes.filtros, reservas.ver, etc.)")
print("     deben crearse manualmente en los archivos .py de routes/")
print("  3. Reinicia Flask después de aplicar los cambios")
print("=" * 60)