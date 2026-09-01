"""
Modelo de Notificacion - LibroVivo
"""
from app.database import ejecutar_consulta


class Notificacion:
    """Representa una notificacion para un usuario"""
    
    def __init__(self, id=None, usuario_id=None, tipo=None, mensaje=None,
                 fecha_envio=None, leida=False, email_enviado=False, relacion_id=None):
        self.id = id
        self.usuario_id = usuario_id
        self.tipo = tipo
        self.mensaje = mensaje
        self.fecha_envio = fecha_envio
        self.leida = leida
        self.email_enviado = email_enviado
        self.relacion_id = relacion_id
    
    @staticmethod
    def obtener_por_id(notificacion_id):
        """Obtiene una notificacion por su ID"""
        sql = """
            SELECT n.*, u.nombre as usuario_nombre, u.apellido as usuario_apellido
            FROM notificaciones n
            JOIN usuarios u ON n.usuario_id = u.id
            WHERE n.id = %s
        """
        return ejecutar_consulta(sql, (notificacion_id,), fetchone=True)
    
    @staticmethod
    def listar_por_usuario(usuario_id, solo_no_leidas=False, limite=None):
        """Lista notificaciones de un usuario"""
        sql = """
            SELECT * FROM notificaciones 
            WHERE usuario_id = %s
        """
        params = [usuario_id]
        
        if solo_no_leidas:
            sql += " AND leida = FALSE"
        
        sql += " ORDER BY fecha_envio DESC"
        
        if limite:
            sql += " LIMIT %s"
            params.append(limite)
        
        return ejecutar_consulta(sql, tuple(params), fetchall=True) or []
    
    @staticmethod
    def contar_no_leidas(usuario_id):
        """Cuenta notificaciones no leidas de un usuario"""
        sql = """
            SELECT COUNT(*) as total FROM notificaciones 
            WHERE usuario_id = %s AND leida = FALSE
        """
        resultado = ejecutar_consulta(sql, (usuario_id,), fetchone=True)
        return resultado['total'] if resultado else 0
    
    @staticmethod
    def crear(usuario_id, tipo, mensaje, relacion_id=None):
        """Crea una nueva notificacion"""
        sql = """
            INSERT INTO notificaciones (usuario_id, tipo, mensaje, relacion_id)
            VALUES (%s, %s, %s, %s)
        """
        return ejecutar_consulta(sql, (usuario_id, tipo, mensaje, relacion_id), commit=True)
    
    @staticmethod
    def marcar_leida(notificacion_id):
        """Marca una notificacion como leida"""
        sql = "UPDATE notificaciones SET leida = TRUE WHERE id = %s"
        return ejecutar_consulta(sql, (notificacion_id,), commit=True)
    
    @staticmethod
    def marcar_todas_leidas(usuario_id):
        """Marca todas las notificaciones de un usuario como leidas"""
        sql = "UPDATE notificaciones SET leida = TRUE WHERE usuario_id = %s"
        return ejecutar_consulta(sql, (usuario_id,), commit=True)
    
    @staticmethod
    def marcar_email_enviado(notificacion_id):
        """Marca que se envio el correo de la notificacion"""
        sql = "UPDATE notificaciones SET email_enviado = TRUE WHERE id = %s"
        return ejecutar_consulta(sql, (notificacion_id,), commit=True)
    
    @staticmethod
    def eliminar(notificacion_id):
        """Elimina una notificacion"""
        sql = "DELETE FROM notificaciones WHERE id = %s"
        return ejecutar_consulta(sql, (notificacion_id,), commit=True)
    
    @staticmethod
    def eliminar_antiguas(dias=30):
        """Elimina notificaciones antiguas (mas de N dias)"""
        sql = """
            DELETE FROM notificaciones 
            WHERE fecha_envio < DATE_SUB(NOW(), INTERVAL %s DAY)
            AND leida = TRUE
        """
        return ejecutar_consulta(sql, (dias,), commit=True)
    
    @staticmethod
    def listar_pendientes_email():
        """Lista notificaciones que aun no se han enviado por email"""
        sql = """
            SELECT n.*, u.email, u.nombre as usuario_nombre
            FROM notificaciones n
            JOIN usuarios u ON n.usuario_id = u.id
            WHERE n.email_enviado = FALSE
            AND u.activo = 1
            ORDER BY n.fecha_envio ASC
        """
        return ejecutar_consulta(sql, fetchall=True) or []
