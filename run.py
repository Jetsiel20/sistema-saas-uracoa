"""
Punto de entrada de la aplicación
Sistema SaaS - Hospital Tipo 1 Uracoa
J&S Software Inteligentes
"""
import os
from dotenv import load_dotenv
from saas import create_app

# Cargar variables de entorno
load_dotenv()

# Obtener configuración del entorno
config_name = os.getenv('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    # DEBUG solo activo en desarrollo, NUNCA en producción
    is_debug = os.getenv('FLASK_ENV', 'development') == 'development'
    
    app.run(
        host='0.0.0.0',
        port=int(os.getenv('PORT', 5000)),
        debug=is_debug
    )
