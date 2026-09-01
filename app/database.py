"""
Conexion y funciones de base de datos MySQL - LibroVivo
Consultas SQL puras (sin ORM)
"""
import mysql.connector
from mysql.connector import Error
from app.config import Config


def get_connection():
    """Obtiene una conexion a la base de datos MySQL"""
    try:
        connection = mysql.connector.connect(
            host=Config.MYSQL_HOST,
            port=Config.MYSQL_PORT,
            user=Config.MYSQL_USER,
            password=Config.MYSQL_PASSWORD,
            database=Config.MYSQL_DB,
            charset='utf8mb4',
            collation='utf8mb4_unicode_ci'
        )
        return connection
    except Error as e:
        print(f"Error al conectar a MySQL: {e}")
        return None


def ejecutar_consulta(sql, params=None, fetchone=False, fetchall=False, commit=False):
    """
    Ejecuta una consulta SQL
    
    Args:
        sql: Consulta SQL
        params: Tupla de parametros
        fetchone: Retorna un solo registro
        fetchall: Retorna todos los registros
        commit: Hace commit si es INSERT/UPDATE/DELETE
    
    Returns:
        Resultado de la consulta o None
    """
    connection = get_connection()
    if not connection:
        return None
    
    cursor = None
    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        
        if commit:
            connection.commit()
            return cursor.lastrowid
        
        if fetchone:
            return cursor.fetchone()
        
        if fetchall:
            return cursor.fetchall()
        
        return True
        
    except Error as e:
        print(f"Error en consulta SQL: {e}")
        print(f"SQL: {sql}")
        print(f"Params: {params}")
        return None
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def ejecutar_transaccion(consultas):
    """
    Ejecuta multiples consultas en una transaccion
    
    Args:
        consultas: Lista de tuplas (sql, params)
    
    Returns:
        True si exitoso, False si fallo
    """
    connection = get_connection()
    if not connection:
        return False
    
    cursor = None
    try:
        cursor = connection.cursor(dictionary=True)
        
        for sql, params in consultas:
            cursor.execute(sql, params or ())
        
        connection.commit()
        return True
        
    except Error as e:
        print(f"Error en transaccion: {e}")
        connection.rollback()
        return False
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def verificar_conexion():
    """Verifica si la conexion a la base de datos funciona"""
    connection = get_connection()
    if connection:
        connection.close()
        return True
    return False
