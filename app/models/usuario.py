"""
Modelo de Usuario - LibroVivo
"""
from app.database import ejecutar_consulta


class Usuario:
    """Representa un usuario del sistema"""
    
    def __init__(self, id=None, nombre=None, apellido=None, email=None,
                 password_hash=None, rol=None, documento=None, telefono=None,
                 foto_perfil=None, activo=True, fecha_registro=None):
        self.id = id
        self.nombre = nombre
        self.apellido = apellido
        self.email = email
        self.password_hash = password_hash
        self.rol = rol
        self.documento = documento
        self.telefono = telefono
        self.foto_perfil = foto_perfil
        self.activo = activo
        self.fecha_registro = fecha_registro
    
    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"
    
    @staticmethod
    def obtener_por_id(usuario_id):
        """Obtiene un usuario por su ID"""
        sql = """
            SELECT id, nombre, apellido, email, password_hash, rol,
                   documento, telefono, foto_perfil, activo, fecha_registro
            FROM usuarios WHERE id = %s
        """
        resultado = ejecutar_consulta(sql, (usuario_id,), fetchone=True)
        if resultado:
            return Usuario(**resultado)
        return None
    
    @staticmethod
    def obtener_por_email(email):
        """Obtiene un usuario por su email"""
        sql = """
            SELECT id, nombre, apellido, email, password_hash, rol,
                   documento, telefono, foto_perfil, activo, fecha_registro
            FROM usuarios WHERE email = %s AND activo = 1
        """
        resultado = ejecutar_consulta(sql, (email,), fetchone=True)
        if resultado:
            return Usuario(**resultado)
        return None
    
    @staticmethod
    def listar_todos(rol=None, activo=None, pagina=1, por_pagina=10):
        """Lista usuarios con filtros opcionales"""
        sql = """
            SELECT id, nombre, apellido, email, rol, documento,
                   telefono, foto_perfil, activo, fecha_registro
            FROM usuarios WHERE 1=1
        """
        params = []
        
        if rol:
            sql += " AND rol = %s"
            params.append(rol)
        
        if activo is not None:
            sql += " AND activo = %s"
            params.append(activo)
        
        sql += " ORDER BY fecha_registro DESC LIMIT %s OFFSET %s"
        params.extend([por_pagina, (pagina - 1) * por_pagina])
        
        return ejecutar_consulta(sql, tuple(params), fetchall=True) or []
    
    @staticmethod
    def contar(rol=None, activo=None):
        """Cuenta usuarios con filtros"""
        sql = "SELECT COUNT(*) as total FROM usuarios WHERE 1=1"
        params = []
        
        if rol:
            sql += " AND rol = %s"
            params.append(rol)
        
        if activo is not None:
            sql += " AND activo = %s"
            params.append(activo)
        
        resultado = ejecutar_consulta(sql, tuple(params), fetchone=True)
        return resultado['total'] if resultado else 0
    
    @staticmethod
    def crear(nombre, apellido, email, password_hash, rol, documento=None,
              telefono=None, foto_perfil=None):
        """Crea un nuevo usuario"""
        sql = """
            INSERT INTO usuarios (nombre, apellido, email, password_hash, rol,
                                  documento, telefono, foto_perfil)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        return ejecutar_consulta(sql, (nombre, apellido, email, password_hash,
                                        rol, documento, telefono, foto_perfil),
                                  commit=True)
    
    @staticmethod
    def actualizar(usuario_id, **kwargs):
        """Actualiza datos de un usuario"""
        campos_permitidos = ['nombre', 'apellido', 'email', 'rol', 'documento',
                             'telefono', 'foto_perfil', 'activo']
        
        campos = []
        valores = []
        
        for campo, valor in kwargs.items():
            if campo in campos_permitidos:
                campos.append(f"{campo} = %s")
                valores.append(valor)
        
        if not campos:
            return False
        
        sql = f"UPDATE usuarios SET {', '.join(campos)} WHERE id = %s"
        valores.append(usuario_id)
        
        return ejecutar_consulta(sql, tuple(valores), commit=True)
    
    @staticmethod
    def eliminar(usuario_id):
        """Elimina logicamente un usuario (desactiva)"""
        sql = "UPDATE usuarios SET activo = 0 WHERE id = %s"
        return ejecutar_consulta(sql, (usuario_id,), commit=True)
    
    @staticmethod
    def cambiar_password(usuario_id, nuevo_password_hash):
        """Cambia la contrasena de un usuario"""
        sql = "UPDATE usuarios SET password_hash = %s WHERE id = %s"
        return ejecutar_consulta(sql, (nuevo_password_hash, usuario_id), commit=True)
