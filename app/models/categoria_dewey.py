"""
Modelo de Categoria Dewey - LibroVivo
"""
from app.database import ejecutar_consulta


class CategoriaDewey:
    """Representa una categoria de clasificacion Dewey"""
    
    def __init__(self, id=None, codigo_dewey=None, nombre=None, descripcion=None):
        self.id = id
        self.codigo_dewey = codigo_dewey
        self.nombre = nombre
        self.descripcion = descripcion
    
    @staticmethod
    def obtener_por_id(categoria_id):
        """Obtiene una categoria por su ID"""
        sql = "SELECT * FROM categorias_dewey WHERE id = %s"
        resultado = ejecutar_consulta(sql, (categoria_id,), fetchone=True)
        if resultado:
            return CategoriaDewey(**resultado)
        return None
    
    @staticmethod
    def listar_todas():
        """Lista todas las categorias Dewey ordenadas por codigo"""
        sql = "SELECT * FROM categorias_dewey ORDER BY codigo_dewey"
        return ejecutar_consulta(sql, fetchall=True) or []
    
    @staticmethod
    def crear(codigo_dewey, nombre, descripcion=None):
        """Crea una nueva categoria"""
        sql = """
            INSERT INTO categorias_dewey (codigo_dewey, nombre, descripcion)
            VALUES (%s, %s, %s)
        """
        return ejecutar_consulta(sql, (codigo_dewey, nombre, descripcion), commit=True)
    
    @staticmethod
    def actualizar(categoria_id, **kwargs):
        """Actualiza una categoria"""
        campos_permitidos = ['codigo_dewey', 'nombre', 'descripcion']
        campos = []
        valores = []
        
        for campo, valor in kwargs.items():
            if campo in campos_permitidos:
                campos.append(f"{campo} = %s")
                valores.append(valor)
        
        if not campos:
            return False
        
        sql = f"UPDATE categorias_dewey SET {', '.join(campos)} WHERE id = %s"
        valores.append(categoria_id)
        
        return ejecutar_consulta(sql, tuple(valores), commit=True)
    
    @staticmethod
    def eliminar(categoria_id):
        """Elimina una categoria (solo si no tiene libros asociados)"""
        sql = "DELETE FROM categorias_dewey WHERE id = %s"
        return ejecutar_consulta(sql, (categoria_id,), commit=True)
