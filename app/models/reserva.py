"""
Modelo de Reserva - LibroVivo
"""
from app.database import ejecutar_consulta


class Reserva:
    """Representa una reserva de libro"""
    
    def __init__(self, id=None, libro_id=None, usuario_id=None,
                 fecha_reserva=None, fecha_vencimiento=None,
                 estado='activa', notificacion_enviada=False):
        self.id = id
        self.libro_id = libro_id
        self.usuario_id = usuario_id
        self.fecha_reserva = fecha_reserva
        self.fecha_vencimiento = fecha_vencimiento
        self.estado = estado
        self.notificacion_enviada = notificacion_enviada
    
    @staticmethod
    def obtener_por_id(reserva_id):
        """Obtiene una reserva por su ID"""
        sql = """
            SELECT r.*, 
                   l.titulo as libro_titulo, l.isbn,
                   u.nombre as usuario_nombre, u.apellido as usuario_apellido, u.email,
                   (SELECT COUNT(*) FROM ejemplares e WHERE e.libro_id = r.libro_id AND e.estado = 'disponible' AND e.activo = 1) as ejemplares_disponibles
            FROM reservas r
            JOIN libros l ON r.libro_id = l.id
            JOIN usuarios u ON r.usuario_id = u.id
            WHERE r.id = %s
        """
        return ejecutar_consulta(sql, (reserva_id,), fetchone=True)
    
    @staticmethod
    def listar_por_usuario(usuario_id, estado=None):
        """Lista reservas de un usuario"""
        sql = """
            SELECT r.*, 
                   l.titulo as libro_titulo, l.isbn, l.portada_url,
                   (SELECT COUNT(*) FROM ejemplares e WHERE e.libro_id = r.libro_id AND e.estado = 'disponible' AND e.activo = 1) as ejemplares_disponibles
            FROM reservas r
            JOIN libros l ON r.libro_id = l.id
            WHERE r.usuario_id = %s
        """
        params = [usuario_id]
        
        if estado:
            sql += " AND r.estado = %s"
            params.append(estado)
        
        sql += " ORDER BY r.fecha_reserva DESC"
        
        return ejecutar_consulta(sql, tuple(params), fetchall=True) or []
    
    @staticmethod
    def listar_activas():
        """Lista reservas activas"""
        sql = """
            SELECT r.*, 
                   l.titulo as libro_titulo,
                   u.nombre as usuario_nombre, u.apellido as usuario_apellido, u.email
            FROM reservas r
            JOIN libros l ON r.libro_id = l.id
            JOIN usuarios u ON r.usuario_id = u.id
            WHERE r.estado = 'activa'
            ORDER BY r.fecha_vencimiento ASC
        """
        return ejecutar_consulta(sql, fetchall=True) or []
    
    @staticmethod
    def listar_disponibles_para_notificar():
        """Lista reservas activas cuyo libro ya tiene ejemplares disponibles"""
        sql = """
            SELECT r.*, 
                   l.titulo as libro_titulo,
                   u.nombre as usuario_nombre, u.apellido as usuario_apellido, u.email
            FROM reservas r
            JOIN libros l ON r.libro_id = l.id
            JOIN usuarios u ON r.usuario_id = u.id
            WHERE r.estado = 'activa'
            AND r.notificacion_enviada = FALSE
            AND (SELECT COUNT(*) FROM ejemplares e 
                 WHERE e.libro_id = r.libro_id AND e.estado = 'disponible' AND e.activo = 1) > 0
        """
        return ejecutar_consulta(sql, fetchall=True) or []
    
    @staticmethod
    def listar_vencidas():
        """Lista reservas que ya vencieron"""
        sql = """
            SELECT r.*, 
                   l.titulo as libro_titulo,
                   u.nombre as usuario_nombre, u.apellido as usuario_apellido
            FROM reservas r
            JOIN libros l ON r.libro_id = l.id
            JOIN usuarios u ON r.usuario_id = u.id
            WHERE r.estado = 'activa' 
            AND r.fecha_vencimiento < CURDATE()
        """
        return ejecutar_consulta(sql, fetchall=True) or []
    
    @staticmethod
    def contar_activas_por_usuario(usuario_id):
        """Cuenta reservas activas de un usuario"""
        sql = """
            SELECT COUNT(*) as total FROM reservas 
            WHERE usuario_id = %s AND estado = 'activa'
        """
        resultado = ejecutar_consulta(sql, (usuario_id,), fetchone=True)
        return resultado['total'] if resultado else 0
    
    @staticmethod
    def crear(libro_id, usuario_id, fecha_vencimiento):
        """Crea una nueva reserva"""
        sql = """
            INSERT INTO reservas (libro_id, usuario_id, fecha_vencimiento)
            VALUES (%s, %s, %s)
        """
        return ejecutar_consulta(sql, (libro_id, usuario_id, fecha_vencimiento), commit=True)
    
    @staticmethod
    def completar(reserva_id):
        """Marca una reserva como completada (el usuario ya retiro el libro)"""
        sql = "UPDATE reservas SET estado = 'completada' WHERE id = %s"
        return ejecutar_consulta(sql, (reserva_id,), commit=True)
    
    @staticmethod
    def cancelar(reserva_id):
        """Cancela una reserva"""
        sql = "UPDATE reservas SET estado = 'cancelada' WHERE id = %s"
        return ejecutar_consulta(sql, (reserva_id,), commit=True)
    
    @staticmethod
    def marcar_vencidas():
        """Marca como vencidas las reservas que pasaron la fecha limite"""
        sql = """
            UPDATE reservas 
            SET estado = 'vencida' 
            WHERE estado = 'activa' AND fecha_vencimiento < CURDATE()
        """
        return ejecutar_consulta(sql, commit=True)
    
    @staticmethod
    def marcar_notificacion_enviada(reserva_id):
        """Marca que se envio notificacion al usuario"""
        sql = "UPDATE reservas SET notificacion_enviada = TRUE WHERE id = %s"
        return ejecutar_consulta(sql, (reserva_id,), commit=True)
    
    @staticmethod
    def usuario_tiene_reserva_activa(libro_id, usuario_id):
        """Verifica si un usuario ya tiene una reserva activa de un libro"""
        sql = """
            SELECT COUNT(*) as total FROM reservas 
            WHERE libro_id = %s AND usuario_id = %s AND estado = 'activa'
        """
        resultado = ejecutar_consulta(sql, (libro_id, usuario_id), fetchone=True)
        return resultado['total'] > 0 if resultado else False
