"""
Modelo de Multa - LibroVivo
"""
from app.database import ejecutar_consulta


class Multa:
    """Representa una multa por retraso en devolucion"""
    
    def __init__(self, id=None, prestamo_id=None, usuario_id=None,
                 dias_retraso=None, monto=None, estado='pendiente',
                 fecha_pago=None, observaciones=None):
        self.id = id
        self.prestamo_id = prestamo_id
        self.usuario_id = usuario_id
        self.dias_retraso = dias_retraso
        self.monto = monto
        self.estado = estado
        self.fecha_pago = fecha_pago
        self.observaciones = observaciones
    
    @staticmethod
    def obtener_por_id(multa_id):
        """Obtiene una multa por su ID"""
        sql = """
            SELECT m.*, 
                   l.titulo as libro_titulo,
                   u.nombre as usuario_nombre, u.apellido as usuario_apellido,
                   p.fecha_devolucion_prevista, p.fecha_devolucion_real
            FROM multas m
            JOIN prestamos p ON m.prestamo_id = p.id
            JOIN ejemplares e ON p.ejemplar_id = e.id
            JOIN libros l ON e.libro_id = l.id
            JOIN usuarios u ON m.usuario_id = u.id
            WHERE m.id = %s
        """
        return ejecutar_consulta(sql, (multa_id,), fetchone=True)
    
    @staticmethod
    def listar_por_usuario(usuario_id, estado=None):
        """Lista multas de un usuario"""
        sql = """
            SELECT m.*, 
                   l.titulo as libro_titulo,
                   p.fecha_devolucion_prevista, p.fecha_devolucion_real
            FROM multas m
            JOIN prestamos p ON m.prestamo_id = p.id
            JOIN ejemplares e ON p.ejemplar_id = e.id
            JOIN libros l ON e.libro_id = l.id
            WHERE m.usuario_id = %s
        """
        params = [usuario_id]
        
        if estado:
            sql += " AND m.estado = %s"
            params.append(estado)
        
        sql += " ORDER BY m.fecha_pago IS NULL DESC, m.id DESC"
        
        return ejecutar_consulta(sql, tuple(params), fetchall=True) or []
    
    @staticmethod
    def listar_pendientes(pagina=1, por_pagina=10):
        """Lista multas pendientes"""
        sql = """
            SELECT m.*, 
                   l.titulo as libro_titulo,
                   u.nombre as usuario_nombre, u.apellido as usuario_apellido,
                   p.fecha_devolucion_prevista
            FROM multas m
            JOIN prestamos p ON m.prestamo_id = p.id
            JOIN ejemplares e ON p.ejemplar_id = e.id
            JOIN libros l ON e.libro_id = l.id
            JOIN usuarios u ON m.usuario_id = u.id
            WHERE m.estado = 'pendiente'
            ORDER BY m.monto DESC
            LIMIT %s OFFSET %s
        """
        return ejecutar_consulta(sql, (por_pagina, (pagina - 1) * por_pagina), fetchall=True) or []
    
    @staticmethod
    def listar_todas(estado=None, pagina=1, por_pagina=10):
        """Lista todas las multas con filtros"""
        sql = """
            SELECT m.*, 
                   l.titulo as libro_titulo,
                   u.nombre as usuario_nombre, u.apellido as usuario_apellido
            FROM multas m
            JOIN prestamos p ON m.prestamo_id = p.id
            JOIN ejemplares e ON p.ejemplar_id = e.id
            JOIN libros l ON e.libro_id = l.id
            JOIN usuarios u ON m.usuario_id = u.id
            WHERE 1=1
        """
        params = []
        
        if estado:
            sql += " AND m.estado = %s"
            params.append(estado)
        
        sql += " ORDER BY m.id DESC LIMIT %s OFFSET %s"
        params.extend([por_pagina, (pagina - 1) * por_pagina])
        
        return ejecutar_consulta(sql, tuple(params), fetchall=True) or []
    
    @staticmethod
    def contar_pendientes_por_usuario(usuario_id):
        """Cuenta multas pendientes de un usuario"""
        sql = """
            SELECT COUNT(*) as total, SUM(monto) as total_monto
            FROM multas 
            WHERE usuario_id = %s AND estado = 'pendiente'
        """
        resultado = ejecutar_consulta(sql, (usuario_id,), fetchone=True)
        return resultado if resultado else {'total': 0, 'total_monto': 0}
    
    @staticmethod
    def tiene_multas_pendientes(usuario_id):
        """Verifica si un usuario tiene multas pendientes"""
        sql = """
            SELECT COUNT(*) as total FROM multas 
            WHERE usuario_id = %s AND estado = 'pendiente'
        """
        resultado = ejecutar_consulta(sql, (usuario_id,), fetchone=True)
        return resultado['total'] > 0 if resultado else False
    
    @staticmethod
    def crear(prestamo_id, usuario_id, dias_retraso, monto):
        """Crea una nueva multa"""
        sql = """
            INSERT INTO multas (prestamo_id, usuario_id, dias_retraso, monto)
            VALUES (%s, %s, %s, %s)
        """
        return ejecutar_consulta(sql, (prestamo_id, usuario_id, dias_retraso, monto), commit=True)
    
    @staticmethod
    def pagar(multa_id, observaciones=None):
        """Registra el pago de una multa"""
        sql = """
            UPDATE multas 
            SET estado = 'pagada', 
                fecha_pago = NOW(),
                observaciones = %s
            WHERE id = %s
        """
        return ejecutar_consulta(sql, (observaciones, multa_id), commit=True)
    
    @staticmethod
    def condonar(multa_id, observaciones=None):
        """Condona una multa"""
        sql = """
            UPDATE multas 
            SET estado = 'condonada',
                observaciones = %s
            WHERE id = %s
        """
        return ejecutar_consulta(sql, (observaciones, multa_id), commit=True)
    
    @staticmethod
    def total_recaudado(fecha_inicio=None, fecha_fin=None):
        """Obtiene el total recaudado en multas"""
        sql = """
            SELECT SUM(monto) as total FROM multas 
            WHERE estado = 'pagada'
        """
        params = []
        
        if fecha_inicio:
            sql += " AND fecha_pago >= %s"
            params.append(fecha_inicio)
        
        if fecha_fin:
            sql += " AND fecha_pago <= %s"
            params.append(fecha_fin)
        
        resultado = ejecutar_consulta(sql, tuple(params) if params else None, fetchone=True)
        return resultado['total'] if resultado and resultado['total'] else 0
    
    @staticmethod
    def top_morosos(limite=10):
        """Obtiene los usuarios con mas multas pendientes"""
        sql = """
            SELECT u.id, u.nombre, u.apellido, u.email,
                   COUNT(m.id) as total_multas,
                   SUM(m.monto) as total_deuda
            FROM multas m
            JOIN usuarios u ON m.usuario_id = u.id
            WHERE m.estado = 'pendiente'
            GROUP BY u.id
            ORDER BY total_deuda DESC
            LIMIT %s
        """
        return ejecutar_consulta(sql, (limite,), fetchall=True) or []
