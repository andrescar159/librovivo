"""
Modelo de Ejemplar - LibroVivo
"""
from app.database import ejecutar_consulta


class Ejemplar:
    """Representa un ejemplar fisico de un libro"""
    
    def __init__(self, id=None, libro_id=None, codigo_barras=None,
                 estado='disponible', es_prestable=True, ubicacion=None, activo=True):
        self.id = id
        self.libro_id = libro_id
        self.codigo_barras = codigo_barras
        self.estado = estado
        self.es_prestable = es_prestable
        self.ubicacion = ubicacion
        self.activo = activo
    
    @staticmethod
    def obtener_por_id(ejemplar_id):
        """Obtiene un ejemplar por su ID"""
        sql = """
            SELECT e.*, l.titulo as libro_titulo, l.isbn
            FROM ejemplares e
            JOIN libros l ON e.libro_id = l.id
            WHERE e.id = %s
        """
        return ejecutar_consulta(sql, (ejemplar_id,), fetchone=True)
    
    @staticmethod
    def obtener_por_codigo(codigo_barras):
        """Obtiene un ejemplar por su codigo de barras"""
        sql = """
            SELECT e.*, l.titulo as libro_titulo, l.isbn
            FROM ejemplares e
            JOIN libros l ON e.libro_id = l.id
            WHERE e.codigo_barras = %s
        """
        return ejecutar_consulta(sql, (codigo_barras,), fetchone=True)
    
    @staticmethod
    def listar_por_libro(libro_id, activo=None):
        """Lista ejemplares de un libro"""
        sql = """
            SELECT e.*, l.titulo as libro_titulo
            FROM ejemplares e
            JOIN libros l ON e.libro_id = l.id
            WHERE e.libro_id = %s
        """
        params = [libro_id]
        
        if activo is not None:
            sql += " AND e.activo = %s"
            params.append(activo)
        
        sql += " ORDER BY e.codigo_barras"
        
        return ejecutar_consulta(sql, tuple(params), fetchall=True) or []
    
    @staticmethod
    def listar_disponibles(libro_id=None, es_prestable=None):
        """Lista ejemplares disponibles para prestamo"""
        sql = """
            SELECT e.*, l.titulo as libro_titulo, l.isbn
            FROM ejemplares e
            JOIN libros l ON e.libro_id = l.id
            WHERE e.estado = 'disponible' AND e.activo = 1
        """
        params = []
        
        if libro_id:
            sql += " AND e.libro_id = %s"
            params.append(libro_id)
        
        if es_prestable is not None:
            sql += " AND e.es_prestable = %s"
            params.append(es_prestable)
        
        sql += " ORDER BY l.titulo, e.codigo_barras"
        
        return ejecutar_consulta(sql, tuple(params), fetchall=True) or []
    
    @staticmethod
    def contar_por_libro(libro_id, estado=None):
        """Cuenta ejemplares de un libro"""
        sql = "SELECT COUNT(*) as total FROM ejemplares WHERE libro_id = %s AND activo = 1"
        params = [libro_id]
        
        if estado:
            sql += " AND estado = %s"
            params.append(estado)
        
        resultado = ejecutar_consulta(sql, tuple(params), fetchone=True)
        return resultado['total'] if resultado else 0
    
    @staticmethod
    def crear(libro_id, codigo_barras, es_prestable=True, ubicacion=None):
        """Crea un nuevo ejemplar"""
        sql = """
            INSERT INTO ejemplares (libro_id, codigo_barras, es_prestable, ubicacion)
            VALUES (%s, %s, %s, %s)
        """
        return ejecutar_consulta(sql, (libro_id, codigo_barras, es_prestable, ubicacion), commit=True)
    
    @staticmethod
    def actualizar(ejemplar_id, **kwargs):
        """Actualiza un ejemplar"""
        campos_permitidos = ['codigo_barras', 'estado', 'es_prestable', 'ubicacion', 'activo']
        campos = []
        valores = []
        
        for campo, valor in kwargs.items():
            if campo in campos_permitidos:
                campos.append(f"{campo} = %s")
                valores.append(valor)
        
        if not campos:
            return False
        
        sql = f"UPDATE ejemplares SET {', '.join(campos)} WHERE id = %s"
        valores.append(ejemplar_id)
        
        return ejecutar_consulta(sql, tuple(valores), commit=True)
    
    @staticmethod
    def cambiar_estado(ejemplar_id, nuevo_estado):
        """Cambia el estado de un ejemplar"""
        sql = "UPDATE ejemplares SET estado = %s WHERE id = %s"
        return ejecutar_consulta(sql, (nuevo_estado, ejemplar_id), commit=True)
    
    @staticmethod
    def eliminar(ejemplar_id):
        """Elimina logicamente un ejemplar"""
        sql = "UPDATE ejemplares SET activo = 0 WHERE id = %s"
        return ejecutar_consulta(sql, (ejemplar_id,), commit=True)
