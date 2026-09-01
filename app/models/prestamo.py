"""
Modelo de Prestamo - LibroVivo
"""
from app.database import ejecutar_consulta


class Prestamo:
    """Representa un prestamo de libro"""
    
    def __init__(self, id=None, ejemplar_id=None, usuario_id=None,
                 bibliotecario_id=None, fecha_prestamo=None,
                 fecha_devolucion_prevista=None, fecha_devolucion_real=None,
                 estado='activo', renovaciones_usadas=0, observaciones=None):
        self.id = id
        self.ejemplar_id = ejemplar_id
        self.usuario_id = usuario_id
        self.bibliotecario_id = bibliotecario_id
        self.fecha_prestamo = fecha_prestamo
        self.fecha_devolucion_prevista = fecha_devolucion_prevista
        self.fecha_devolucion_real = fecha_devolucion_real
        self.estado = estado
        self.renovaciones_usadas = renovaciones_usadas
        self.observaciones = observaciones
    
    @staticmethod
    def obtener_por_id(prestamo_id):
        """Obtiene un prestamo por su ID con informacion completa"""
        sql = """
            SELECT p.*, 
                   l.titulo as libro_titulo, l.isbn,
                   e.codigo_barras,
                   u.nombre as usuario_nombre, u.apellido as usuario_apellido,
                   b.nombre as bibliotecario_nombre, b.apellido as bibliotecario_apellido
            FROM prestamos p
            JOIN ejemplares e ON p.ejemplar_id = e.id
            JOIN libros l ON e.libro_id = l.id
            JOIN usuarios u ON p.usuario_id = u.id
            JOIN usuarios b ON p.bibliotecario_id = b.id
            WHERE p.id = %s
        """
        return ejecutar_consulta(sql, (prestamo_id,), fetchone=True)
    
    @staticmethod
    def listar_por_usuario(usuario_id, estado=None):
        """Lista prestamos de un usuario"""
        sql = """
            SELECT p.*, 
                   l.titulo as libro_titulo, l.isbn,
                   e.codigo_barras
            FROM prestamos p
            JOIN ejemplares e ON p.ejemplar_id = e.id
            JOIN libros l ON e.libro_id = l.id
            WHERE p.usuario_id = %s
        """
        params = [usuario_id]
        
        if estado:
            sql += " AND p.estado = %s"
            params.append(estado)
        
        sql += " ORDER BY p.fecha_prestamo DESC"
        
        return ejecutar_consulta(sql, tuple(params), fetchall=True) or []
    
    @staticmethod
    def listar_activos(pagina=1, por_pagina=10):
        """Lista prestamos activos"""
        sql = """
            SELECT p.*, 
                   l.titulo as libro_titulo,
                   u.nombre as usuario_nombre, u.apellido as usuario_apellido
            FROM prestamos p
            JOIN ejemplares e ON p.ejemplar_id = e.id
            JOIN libros l ON e.libro_id = l.id
            JOIN usuarios u ON p.usuario_id = u.id
            WHERE p.estado = 'activo'
            ORDER BY p.fecha_devolucion_prevista ASC
            LIMIT %s OFFSET %s
        """
        return ejecutar_consulta(sql, (por_pagina, (pagina - 1) * por_pagina), fetchall=True) or []
    
    @staticmethod
    def listar_vencidos():
        """Lista prestamos vencidos (fecha prevista < hoy y estado activo)"""
        sql = """
            SELECT p.*, 
                   l.titulo as libro_titulo,
                   u.nombre as usuario_nombre, u.apellido as usuario_apellido,
                   DATEDIFF(CURDATE(), p.fecha_devolucion_prevista) as dias_vencido
            FROM prestamos p
            JOIN ejemplares e ON p.ejemplar_id = e.id
            JOIN libros l ON e.libro_id = l.id
            JOIN usuarios u ON p.usuario_id = u.id
            WHERE p.estado = 'activo' 
            AND p.fecha_devolucion_prevista < CURDATE()
            ORDER BY p.fecha_devolucion_prevista ASC
        """
        return ejecutar_consulta(sql, fetchall=True) or []
    
    @staticmethod
    def listar_vencen_hoy_o_mañana(dias=1):
        """Lista prestamos que vencen en los proximos N dias"""
        sql = """
            SELECT p.*, 
                   l.titulo as libro_titulo,
                   u.nombre as usuario_nombre, u.apellido as usuario_apellido, u.email
            FROM prestamos p
            JOIN ejemplares e ON p.ejemplar_id = e.id
            JOIN libros l ON e.libro_id = l.id
            JOIN usuarios u ON p.usuario_id = u.id
            WHERE p.estado = 'activo' 
            AND p.fecha_devolucion_prevista BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL %s DAY)
            ORDER BY p.fecha_devolucion_prevista ASC
        """
        return ejecutar_consulta(sql, (dias,), fetchall=True) or []
    
    @staticmethod
    def contar_activos_por_usuario(usuario_id):
        """Cuenta prestamos activos de un usuario"""
        sql = """
            SELECT COUNT(*) as total FROM prestamos 
            WHERE usuario_id = %s AND estado = 'activo'
        """
        resultado = ejecutar_consulta(sql, (usuario_id,), fetchone=True)
        return resultado['total'] if resultado else 0
    
    @staticmethod
    def crear(ejemplar_id, usuario_id, bibliotecario_id, fecha_devolucion_prevista):
        """Crea un nuevo prestamo"""
        sql = """
            INSERT INTO prestamos (ejemplar_id, usuario_id, bibliotecario_id, 
                                  fecha_devolucion_prevista)
            VALUES (%s, %s, %s, %s)
        """
        return ejecutar_consulta(sql, (ejemplar_id, usuario_id, bibliotecario_id,
                                        fecha_devolucion_prevista), commit=True)
    
    @staticmethod
    def devolver(prestamo_id, observaciones=None):
        """Registra la devolucion de un prestamo"""
        sql = """
            UPDATE prestamos 
            SET estado = 'devuelto', 
                fecha_devolucion_real = NOW(),
                observaciones = %s
            WHERE id = %s
        """
        return ejecutar_consulta(sql, (observaciones, prestamo_id), commit=True)
    
    @staticmethod
    def marcar_vencido(prestamo_id):
        """Marca un prestamo como vencido"""
        sql = "UPDATE prestamos SET estado = 'vencido' WHERE id = %s"
        return ejecutar_consulta(sql, (prestamo_id,), commit=True)
    
    @staticmethod
    def marcar_perdido(prestamo_id):
        """Marca un prestamo como perdido"""
        sql = "UPDATE prestamos SET estado = 'perdido' WHERE id = %s"
        return ejecutar_consulta(sql, (prestamo_id,), commit=True)
    
    @staticmethod
    def renovar(prestamo_id, nueva_fecha_devolucion):
        """Renueva un prestamo"""
        sql = """
            UPDATE prestamos 
            SET fecha_devolucion_prevista = %s,
                renovaciones_usadas = renovaciones_usadas + 1
            WHERE id = %s
        """
        return ejecutar_consulta(sql, (nueva_fecha_devolucion, prestamo_id), commit=True)
    
    @staticmethod
    def contar_prestamos_mes(mes, anio):
        """Cuenta prestamos de un mes especifico"""
        sql = """
            SELECT COUNT(*) as total FROM prestamos 
            WHERE MONTH(fecha_prestamo) = %s AND YEAR(fecha_prestamo) = %s
        """
        resultado = ejecutar_consulta(sql, (mes, anio), fetchone=True)
        return resultado['total'] if resultado else 0
    
    @staticmethod
    def estadisticas_mensuales(anio):
        """Obtiene estadisticas de prestamos por mes"""
        sql = """
            SELECT MONTH(fecha_prestamo) as mes, COUNT(*) as total
            FROM prestamos 
            WHERE YEAR(fecha_prestamo) = %s
            GROUP BY MONTH(fecha_prestamo)
            ORDER BY mes
        """
        return ejecutar_consulta(sql, (anio,), fetchall=True) or []
