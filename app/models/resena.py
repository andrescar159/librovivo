"""
Modelo de Resena - LibroVivo
"""
from app.database import ejecutar_consulta


class Resena:
    """Representa una resena/calificacion de un libro"""
    
    def __init__(self, id=None, libro_id=None, usuario_id=None,
                 calificacion=None, comentario=None, fecha=None, activo=True):
        self.id = id
        self.libro_id = libro_id
        self.usuario_id = usuario_id
        self.calificacion = calificacion
        self.comentario = comentario
        self.fecha = fecha
        self.activo = activo
    
    @staticmethod
    def obtener_por_id(resena_id):
        """Obtiene una resena por su ID"""
        sql = """
            SELECT r.*, 
                   l.titulo as libro_titulo,
                   u.nombre as usuario_nombre, u.apellido as usuario_apellido
            FROM resenas r
            JOIN libros l ON r.libro_id = l.id
            JOIN usuarios u ON r.usuario_id = u.id
            WHERE r.id = %s
        """
        return ejecutar_consulta(sql, (resena_id,), fetchone=True)
    
    @staticmethod
    def listar_por_libro(libro_id, solo_activas=True):
        """Lista resenas de un libro"""
        sql = """
            SELECT r.*, 
                   u.nombre as usuario_nombre, u.apellido as usuario_apellido,
                   u.foto_perfil
            FROM resenas r
            JOIN usuarios u ON r.usuario_id = u.id
            WHERE r.libro_id = %s
        """
        params = [libro_id]
        
        if solo_activas:
            sql += " AND r.activo = 1"
        
        sql += " ORDER BY r.fecha DESC"
        
        return ejecutar_consulta(sql, tuple(params), fetchall=True) or []
    
    @staticmethod
    def listar_por_usuario(usuario_id):
        """Lista resenas de un usuario"""
        sql = """
            SELECT r.*, 
                   l.titulo as libro_titulo, l.portada_url
            FROM resenas r
            JOIN libros l ON r.libro_id = l.id
            WHERE r.usuario_id = %s AND r.activo = 1
            ORDER BY r.fecha DESC
        """
        return ejecutar_consulta(sql, (usuario_id,), fetchall=True) or []
    
    @staticmethod
    def listar_todas(solo_activas=True, pagina=1, por_pagina=10):
        """Lista todas las resenas (para moderacion)"""
        sql = """
            SELECT r.*, 
                   l.titulo as libro_titulo,
                   u.nombre as usuario_nombre, u.apellido as usuario_apellido
            FROM resenas r
            JOIN libros l ON r.libro_id = l.id
            JOIN usuarios u ON r.usuario_id = u.id
            WHERE 1=1
        """
        params = []
        
        if solo_activas:
            sql += " AND r.activo = 1"
        
        sql += " ORDER BY r.fecha DESC LIMIT %s OFFSET %s"
        params.extend([por_pagina, (pagina - 1) * por_pagina])
        
        return ejecutar_consulta(sql, tuple(params), fetchall=True) or []
    
    @staticmethod
    def obtener_promedio_libro(libro_id):
        """Obtiene la calificacion promedio de un libro"""
        sql = """
            SELECT AVG(calificacion) as promedio, COUNT(*) as total
            FROM resenas 
            WHERE libro_id = %s AND activo = 1
        """
        resultado = ejecutar_consulta(sql, (libro_id,), fetchone=True)
        if resultado:
            return {
                'promedio': round(resultado['promedio'], 1) if resultado['promedio'] else 0,
                'total': resultado['total']
            }
        return {'promedio': 0, 'total': 0}
    
    @staticmethod
    def usuario_ha_resenado(libro_id, usuario_id):
        """Verifica si un usuario ya reseno un libro"""
        sql = """
            SELECT COUNT(*) as total FROM resenas 
            WHERE libro_id = %s AND usuario_id = %s AND activo = 1
        """
        resultado = ejecutar_consulta(sql, (libro_id, usuario_id), fetchone=True)
        return resultado['total'] > 0 if resultado else False
    
    @staticmethod
    def crear(libro_id, usuario_id, calificacion, comentario=None):
        """Crea una nueva resena"""
        sql = """
            INSERT INTO resenas (libro_id, usuario_id, calificacion, comentario)
            VALUES (%s, %s, %s, %s)
        """
        return ejecutar_consulta(sql, (libro_id, usuario_id, calificacion, comentario), commit=True)
    
    @staticmethod
    def actualizar(resena_id, calificacion=None, comentario=None):
        """Actualiza una resena"""
        campos = []
        valores = []
        
        if calificacion is not None:
            campos.append("calificacion = %s")
            valores.append(calificacion)
        
        if comentario is not None:
            campos.append("comentario = %s")
            valores.append(comentario)
        
        if not campos:
            return False
        
        sql = f"UPDATE resenas SET {', '.join(campos)} WHERE id = %s"
        valores.append(resena_id)
        
        return ejecutar_consulta(sql, tuple(valores), commit=True)
    
    @staticmethod
    def eliminar(resena_id):
        """Elimina logicamente una resena (moderacion)"""
        sql = "UPDATE resenas SET activo = 0 WHERE id = %s"
        return ejecutar_consulta(sql, (resena_id,), commit=True)
    
    @staticmethod
    def restaurar(resena_id):
        """Restaura una resena eliminada"""
        sql = "UPDATE resenas SET activo = 1 WHERE id = %s"
        return ejecutar_consulta(sql, (resena_id,), commit=True)
    
    @staticmethod
    def contar_por_libro(libro_id):
        """Cuenta resenas de un libro"""
        sql = """
            SELECT COUNT(*) as total FROM resenas 
            WHERE libro_id = %s AND activo = 1
        """
        resultado = ejecutar_consulta(sql, (libro_id,), fetchone=True)
        return resultado['total'] if resultado else 0
