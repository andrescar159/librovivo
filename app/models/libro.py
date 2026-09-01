"""
Modelo de Libro - LibroVivo
"""
from app.database import ejecutar_consulta


class Libro:
    """Representa un libro en el sistema"""
    
    def __init__(self, id=None, categoria_id=None, isbn=None, titulo=None,
                 editorial=None, anio_publicacion=None, descripcion=None,
                 portada_url=None, area_conocimiento=None, activo=True):
        self.id = id
        self.categoria_id = categoria_id
        self.isbn = isbn
        self.titulo = titulo
        self.editorial = editorial
        self.anio_publicacion = anio_publicacion
        self.descripcion = descripcion
        self.portada_url = portada_url
        self.area_conocimiento = area_conocimiento
        self.activo = activo
    
    @staticmethod
    def obtener_por_id(libro_id):
        """Obtiene un libro por su ID con informacion de categoria"""
        sql = """
            SELECT l.*, c.nombre as categoria_nombre, c.codigo_dewey
            FROM libros l
            LEFT JOIN categorias_dewey c ON l.categoria_id = c.id
            WHERE l.id = %s
        """
        return ejecutar_consulta(sql, (libro_id,), fetchone=True)
    
    @staticmethod
    def obtener_por_isbn(isbn):
        """Obtiene un libro por su ISBN"""
        sql = "SELECT * FROM libros WHERE isbn = %s"
        return ejecutar_consulta(sql, (isbn,), fetchone=True)
    
    @staticmethod
    def listar_todos(activo=None, categoria_id=None, pagina=1, por_pagina=10):
        """Lista libros con filtros"""
        sql = """
            SELECT l.*, c.nombre as categoria_nombre, c.codigo_dewey,
                   (SELECT COUNT(*) FROM ejemplares e WHERE e.libro_id = l.id AND e.activo = 1) as total_ejemplares,
                   (SELECT COUNT(*) FROM ejemplares e WHERE e.libro_id = l.id AND e.estado = 'disponible' AND e.activo = 1) as ejemplares_disponibles
            FROM libros l
            LEFT JOIN categorias_dewey c ON l.categoria_id = c.id
            WHERE 1=1
        """
        params = []
        
        if activo is not None:
            sql += " AND l.activo = %s"
            params.append(activo)
        
        if categoria_id:
            sql += " AND l.categoria_id = %s"
            params.append(categoria_id)
        
        sql += " ORDER BY l.titulo LIMIT %s OFFSET %s"
        params.extend([por_pagina, (pagina - 1) * por_pagina])
        
        return ejecutar_consulta(sql, tuple(params), fetchall=True) or []
    
    @staticmethod
    def buscar(query, categoria_id=None):
        """Busca libros por titulo, autor o ISBN"""
        sql = """
            SELECT DISTINCT l.*, c.nombre as categoria_nombre, c.codigo_dewey,
                   (SELECT COUNT(*) FROM ejemplares e WHERE e.libro_id = l.id AND e.activo = 1) as total_ejemplares,
                   (SELECT COUNT(*) FROM ejemplares e WHERE e.libro_id = l.id AND e.estado = 'disponible' AND e.activo = 1) as ejemplares_disponibles
            FROM libros l
            LEFT JOIN categorias_dewey c ON l.categoria_id = c.id
            LEFT JOIN libros_autores la ON l.id = la.libro_id
            LEFT JOIN autores a ON la.autor_id = a.id
            WHERE l.activo = 1
            AND (l.titulo LIKE %s OR l.isbn LIKE %s OR a.nombre LIKE %s OR l.area_conocimiento LIKE %s)
        """
        like_query = f"%{query}%"
        params = [like_query, like_query, like_query, like_query]
        
        if categoria_id:
            sql += " AND l.categoria_id = %s"
            params.append(categoria_id)
        
        sql += " ORDER BY l.titulo"
        
        return ejecutar_consulta(sql, tuple(params), fetchall=True) or []
    
    @staticmethod
    def contar(activo=None, categoria_id=None):
        """Cuenta libros con filtros"""
        sql = "SELECT COUNT(*) as total FROM libros WHERE 1=1"
        params = []
        
        if activo is not None:
            sql += " AND activo = %s"
            params.append(activo)
        
        if categoria_id:
            sql += " AND categoria_id = %s"
            params.append(categoria_id)
        
        resultado = ejecutar_consulta(sql, tuple(params), fetchone=True)
        return resultado['total'] if resultado else 0
    
    @staticmethod
    def crear(categoria_id, isbn, titulo, editorial=None, anio_publicacion=None,
              descripcion=None, portada_url=None, area_conocimiento=None):
        """Crea un nuevo libro"""
        sql = """
            INSERT INTO libros (categoria_id, isbn, titulo, editorial, anio_publicacion,
                               descripcion, portada_url, area_conocimiento)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        return ejecutar_consulta(sql, (categoria_id, isbn, titulo, editorial,
                                        anio_publicacion, descripcion, portada_url,
                                        area_conocimiento), commit=True)
    
    @staticmethod
    def actualizar(libro_id, **kwargs):
        """Actualiza un libro"""
        campos_permitidos = ['categoria_id', 'isbn', 'titulo', 'editorial',
                             'anio_publicacion', 'descripcion', 'portada_url',
                             'area_conocimiento', 'activo']
        campos = []
        valores = []
        
        for campo, valor in kwargs.items():
            if campo in campos_permitidos:
                campos.append(f"{campo} = %s")
                valores.append(valor)
        
        if not campos:
            return False
        
        sql = f"UPDATE libros SET {', '.join(campos)} WHERE id = %s"
        valores.append(libro_id)
        
        return ejecutar_consulta(sql, tuple(valores), commit=True)
    
    @staticmethod
    def eliminar(libro_id):
        """Elimina logicamente un libro"""
        sql = "UPDATE libros SET activo = 0 WHERE id = %s"
        return ejecutar_consulta(sql, (libro_id,), commit=True)
    
    @staticmethod
    def obtener_autores(libro_id):
        """Obtiene los autores de un libro"""
        sql = """
            SELECT a.* FROM autores a
            JOIN libros_autores la ON a.id = la.autor_id
            WHERE la.libro_id = %s
        """
        return ejecutar_consulta(sql, (libro_id,), fetchall=True) or []
    
    @staticmethod
    def agregar_autor(libro_id, autor_id):
        """Agrega un autor a un libro"""
        sql = "INSERT INTO libros_autores (libro_id, autor_id) VALUES (%s, %s)"
        return ejecutar_consulta(sql, (libro_id, autor_id), commit=True)
    
    @staticmethod
    def eliminar_autor(libro_id, autor_id):
        """Elimina un autor de un libro"""
        sql = "DELETE FROM libros_autores WHERE libro_id = %s AND autor_id = %s"
        return ejecutar_consulta(sql, (libro_id, autor_id), commit=True)
    
    @staticmethod
    def mas_prestados(limite=5):
        """Obtiene los libros mas prestados"""
        sql = """
            SELECT l.*, c.nombre as categoria_nombre,
                   COUNT(p.id) as total_prestamos
            FROM libros l
            LEFT JOIN categorias_dewey c ON l.categoria_id = c.id
            LEFT JOIN ejemplares e ON l.id = e.libro_id
            LEFT JOIN prestamos p ON e.id = p.ejemplar_id
            WHERE l.activo = 1
            GROUP BY l.id
            ORDER BY total_prestamos DESC
            LIMIT %s
        """
        return ejecutar_consulta(sql, (limite,), fetchall=True) or []
