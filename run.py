"""
LibroVivo - Punto de entrada de la aplicacion
Sistema de Gestion Bibliotecaria
"""
import os
import sys

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app

# Crear instancia de la aplicacion
app = create_app(os.environ.get('FLASK_ENV', 'development'))

if __name__ == '__main__':
    # Verificar conexion a base de datos
    from app.database import verificar_conexion
    
    if not verificar_conexion():
        print("=" * 60)
        print("ADVERTENCIA: No se pudo conectar a MySQL")
        print("Verifica que:")
        print("  1. XAMPP esta ejecutando MySQL")
        print("  2. La base de datos 'librovivo' existe")
        print("  3. Las credenciales en .env son correctas")
        print("=" * 60)
    
    # Ejecutar aplicacion
    app.run(
        host=os.environ.get('FLASK_HOST', '0.0.0.0'),
        port=int(os.environ.get('FLASK_PORT', 5000)),
        debug=os.environ.get('FLASK_DEBUG', 'True').lower() == 'true'
    )