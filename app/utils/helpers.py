"""
Funciones auxiliares - LibroVivo
Utilidades varias para la aplicacion
"""
import os
import re
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
from app.config import Config


def allowed_file(filename):
    """
    Verifica si la extension del archivo es permitida
    
    Args:
        filename: Nombre del archivo
    
    Returns:
        bool: True si es permitido
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def guardar_archivo(archivo, carpeta):
    """
    Guarda un archivo subido en la carpeta correspondiente
    
    Args:
        archivo: Objeto FileStorage de Flask
        carpeta: 'perfiles' o 'portadas'
    
    Returns:
        str: Ruta relativa del archivo guardado, o None si fallo
    """
    if archivo and allowed_file(archivo.filename):
        # Generar nombre unico
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = secure_filename(archivo.filename)
        nombre_base, extension = os.path.splitext(filename)
        nombre_unico = f"{nombre_base}_{timestamp}{extension}"
        
        # Determinar ruta
        if carpeta == 'perfiles':
            ruta = os.path.join(Config.UPLOAD_FOLDER_PERFILES, nombre_unico)
            ruta_relativa = f"uploads/perfiles/{nombre_unico}"
        else:
            ruta = os.path.join(Config.UPLOAD_FOLDER_PORTADAS, nombre_unico)
            ruta_relativa = f"uploads/portadas/{nombre_unico}"
        
        # Guardar archivo
        archivo.save(ruta)
        return ruta_relativa
    
    return None


def eliminar_archivo(ruta_relativa):
    """
    Elimina un archivo del sistema
    
    Args:
        ruta_relativa: Ruta relativa del archivo (ej: uploads/perfiles/foto.jpg)
    
    Returns:
        bool: True si se elimino correctamente
    """
    try:
        ruta_completa = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'static',
            ruta_relativa
        )
        if os.path.exists(ruta_completa):
            os.remove(ruta_completa)
            return True
    except Exception as e:
        print(f"Error al eliminar archivo: {e}")
    
    return False


def formatear_fecha(fecha, formato='%d/%m/%Y'):
    """
    Formatea una fecha para mostrar
    
    Args:
        fecha: Objeto datetime o string
        formato: Formato deseado
    
    Returns:
        str: Fecha formateada
    """
    if fecha is None:
        return ''
    
    if isinstance(fecha, str):
        try:
            fecha = datetime.strptime(fecha, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return fecha
    
    return fecha.strftime(formato)


def formatear_fecha_hora(fecha):
    """
    Formatea fecha y hora
    
    Args:
        fecha: Objeto datetime
    
    Returns:
        str: Fecha y hora formateada
    """
    return formatear_fecha(fecha, '%d/%m/%Y %H:%M')


def formatear_moneda(valor):
    """
    Formatea un valor en pesos colombianos
    
    Args:
        valor: Valor numerico
    
    Returns:
        str: Valor formateado (ej: $5.000)
    """
    if valor is None:
        return '$0'
    
    return f"${valor:,.0f}".replace(',', '.')


def calcular_dias_restantes(fecha_vencimiento):
    """
    Calcula los dias restantes hasta una fecha
    
    Args:
        fecha_vencimiento: Fecha limite
    
    Returns:
        int: Dias restantes (negativo si ya vencio)
    """
    if fecha_vencimiento is None:
        return 0
    
    if isinstance(fecha_vencimiento, str):
        fecha_vencimiento = datetime.strptime(fecha_vencimiento, '%Y-%m-%d %H:%M:%S')
    
    hoy = datetime.now()
    diferencia = fecha_vencimiento - hoy
    
    return diferencia.days


def es_fecha_vencida(fecha_vencimiento):
    """
    Verifica si una fecha ya vencio
    
    Args:
        fecha_vencimiento: Fecha a verificar
    
    Returns:
        bool: True si ya vencio
    """
    return calcular_dias_restantes(fecha_vencimiento) < 0


def validar_email(email):
    """
    Valida formato de correo electronico
    
    Args:
        email: Correo a validar
    
    Returns:
        bool: True si es valido
    """
    patron = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(patron, email) is not None


def validar_documento(documento):
    """
    Valida formato de documento colombiano
    
    Args:
        documento: Numero de documento
    
    Returns:
        bool: True si es valido
    """
    # Permitir solo numeros, entre 6 y 12 digitos
    patron = r'^\d{6,12}$'
    return re.match(patron, documento) is not None


def validar_telefono(telefono):
    """
    Valida formato de telefono colombiano
    
    Args:
        telefono: Numero de telefono
    
    Returns:
        bool: True si es valido
    """
    # Permitir numeros, espacios, guiones y parentesis
    patron = r'^[\d\s\-\(\)\+]{7,15}$'
    return re.match(patron, telefono) is not None


def truncar_texto(texto, longitud=100):
    """
    Trunca un texto a una longitud maxima
    
    Args:
        texto: Texto a truncar
        longitud: Longitud maxima
    
    Returns:
        str: Texto truncado con '...' si es necesario
    """
    if texto and len(texto) > longitud:
        return texto[:longitud] + '...'
    return texto


def generar_codigo_barras():
    """
    Genera un codigo de barras unico para ejemplar
    
    Returns:
        str: Codigo de barras
    """
    import random
    import string
    
    # Formato: LV-XXXXX (LibroVivo + 5 digitos)
    numero = ''.join(random.choices(string.digits, k=5))
    return f"LV-{numero}"


def obtener_mes_nombre(numero_mes):
    """
    Obtiene el nombre del mes en espanol
    
    Args:
        numero_mes: Numero del mes (1-12)
    
    Returns:
        str: Nombre del mes
    """
    meses = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    return meses.get(numero_mes, '')


def calcular_edad(fecha_nacimiento):
    """
    Calcula la edad a partir de la fecha de nacimiento
    
    Args:
        fecha_nacimiento: Fecha de nacimiento
    
    Returns:
        int: Edad en anos
    """
    if fecha_nacimiento is None:
        return 0
    
    if isinstance(fecha_nacimiento, str):
        fecha_nacimiento = datetime.strptime(fecha_nacimiento, '%Y-%m-%d')
    
    hoy = datetime.now()
    edad = hoy.year - fecha_nacimiento.year
    
    # Ajustar si aun no ha cumplido anos este ano
    if (hoy.month, hoy.day) < (fecha_nacimiento.month, fecha_nacimiento.day):
        edad -= 1
    
    return edad


def paginar_lista(lista, pagina, por_pagina):
    """
    Pagina una lista de elementos
    
    Args:
        lista: Lista completa
        pagina: Numero de pagina actual
        por_pagina: Elementos por pagina
    
    Returns:
        tuple: (lista_paginada, total_paginas)
    """
    total = len(lista)
    total_paginas = (total + por_pagina - 1) // por_pagina
    
    inicio = (pagina - 1) * por_pagina
    fin = inicio + por_pagina
    
    return lista[inicio:fin], total_paginas