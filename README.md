# Sistema SaaS - Hospital Tipo 1 Uracoa

![Hospital](https://img.shields.io/badge/Hospital-Tipo%201%20Uracoa-blue)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![Flask](https://img.shields.io/badge/Flask-3.0-green)
![License](https://img.shields.io/badge/License-Proprietary-red)

## 📋 Descripción

Sistema SaaS profesional desarrollado para el Hospital Tipo 1 Uracoa, que permite la gestión integral de:

- **Pacientes**: Registro completo, historias clínicas, seguimiento
- **Citas Médicas**: Programación, confirmación, gestión de agenda
- **Personal Médico**: Médicos, enfermeras, personal administrativo
- **Medicamentos**: Inventario de farmacia, control de stock
- **Reportes**: Estadísticas y análisis del hospital

## 🏗️ Arquitectura

```
sistema_saas/
│
├── saas/                   # Código principal
│   ├── __init__.py        # Factory de la aplicación
│   ├── config.py          # Configuraciones
│   ├── extensions.py      # Extensiones Flask
│   ├── models.py          # Modelos de base de datos
│   │
│   ├── auth/              # Módulo de autenticación
│   │   ├── __init__.py
│   │   ├── routes.py
│   │   └── forms.py
│   │
│   ├── main/              # Módulo principal
│   │   ├── __init__.py
│   │   └── routes.py
│   │
│   ├── templates/         # Templates Jinja2
│   │   ├── base.html
│   │   ├── auth/
│   │   └── main/
│   │
│   └── static/            # Archivos estáticos
│       ├── css/
│       └── js/
│
├── instance/              # Base de datos local
├── migrations/            # Migraciones de BD
├── requirements.txt       # Dependencias Python
├── .env                   # Variables de entorno
├── run.py                 # Punto de entrada
└── README.md
```

## 🚀 Instalación

### Prerrequisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)
- Virtualenv (recomendado)

### Pasos de instalación

1. **Clonar o descargar el proyecto**

2. **Crear entorno virtual**
```powershell
python -m venv env
```

3. **Activar entorno virtual**
```powershell
# Windows PowerShell
.\env\Scripts\Activate.ps1

# Windows CMD
.\env\Scripts\activate.bat
```

4. **Instalar dependencias**
```powershell
pip install -r requirements.txt
```

5. **Configurar variables de entorno**
   
   Editar el archivo `.env` con tus configuraciones:
   ```
   SECRET_KEY=tu-clave-secreta-aqui
   DATABASE_URL=sqlite:///app.db
   ```

6. **Inicializar la base de datos**
```powershell
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

## 🎮 Uso

### Ejecutar en modo desarrollo

```powershell
python run.py
```

La aplicación estará disponible en: `http://localhost:5000`

### Crear primer usuario administrador

Puedes crear un usuario admin mediante la consola Python:

```python
from saas import create_app
from saas.extensions import db
from saas.models import Usuario

app = create_app()
with app.app_context():
    admin = Usuario(
        username='admin',
        email='admin@hospital.com',
        nombre='Administrador',
        apellido='Sistema',
        cedula='00000000',
        rol='admin'
    )
    admin.set_password('admin123')
    db.session.add(admin)
    db.session.commit()
```

## 👥 Roles de Usuario

- **Admin**: Acceso completo al sistema
- **Médico**: Gestión de pacientes, citas, historias clínicas
- **Enfermera**: Registro de signos vitales, apoyo médico
- **Recepcionista**: Gestión de citas, registro de pacientes
- **Farmacia**: Control de inventario de medicamentos
- **Laboratorio**: Gestión de exámenes y resultados

## 🔒 Seguridad

- Autenticación mediante Flask-Login
- Contraseñas hasheadas con Werkzeug
- Protección CSRF en formularios
- Sesiones seguras
- Control de acceso basado en roles

## 📊 Modelos de Base de Datos

### Usuario
- Información personal y credenciales
- Rol y especialidad
- Gestión de permisos

### Paciente
- Datos demográficos
- Información médica básica
- Seguro médico
- Contacto de emergencia

### Cita
- Programación de consultas
- Estados: programada, confirmada, completada, cancelada
- Relación con paciente y médico

### HistoriaClinica
- Motivo de consulta
- Signos vitales
- Diagnóstico y tratamiento
- Prescripciones

### Medicamento
- Inventario de farmacia
- Control de stock
- Alertas de stock bajo

## 🛠️ Tecnologías Utilizadas

- **Backend**: Python 3.8+, Flask 3.0
- **Base de datos**: SQLite (desarrollo) / PostgreSQL (producción)
- **ORM**: SQLAlchemy
- **Frontend**: Bootstrap 5, Bootstrap Icons
- **Autenticación**: Flask-Login
- **Formularios**: Flask-WTF, WTForms
- **Migraciones**: Flask-Migrate

## 📈 Próximas Características

- [ ] Sistema de reportes avanzados
- [ ] Integración con laboratorio
- [ ] Gestión de historias clínicas electrónicas
- [ ] Sistema de facturación
- [ ] Módulo de telemedicina
- [ ] App móvil
- [ ] Integración con equipos médicos
- [ ] Sistema de backup automático

## 👨‍💻 Equipo de Desarrollo

**J&S Software Inteligentes**

- Desarrollador Full Stack Senior: GitHub Copilot
- Product Owner: Santos
- Colaboración: ChatGPT

## 📄 Licencia

Este proyecto es propiedad de J&S Software Inteligentes.  
Todos los derechos reservados © 2025

## 📞 Soporte

Para soporte técnico o consultas:
- Email: soporte@jssoftware.com
- Teléfono: +58 XXX-XXXXXXX

---

**Desarrollado con ❤️ para el Hospital Tipo 1 Uracoa**
