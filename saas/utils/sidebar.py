"""
Utilidades para navegación dinámica por rol
Sistema SaaS - Hospital Tipo 1 Uracoa
"""

def get_menu_for(user):
    """
    Retorna el menú de navegación según el rol del usuario
    
    Args:
        user: Objeto Usuario con propiedad .rol
        
    Returns:
        Lista de diccionarios con: name, url, icon, label
    """
    # Definición de todos los items del menú con sus metadatos
    MENU_ITEMS = {
        'dashboard': {
            'name': 'dashboard',
            'label': 'Dashboard',
            'url': 'main.dashboard',
            'icon': 'bi-speedometer2'
        },
        'doctores': {
            'name': 'doctores',
            'label': 'Doctores',
            'url': 'main.usuarios',
            'icon': 'bi-person-heart'
        },
        'pacientes': {
            'name': 'pacientes',
            'label': 'Pacientes',
            'url': 'main.pacientes',
            'icon': 'bi-people'
        },
        'citas': {
            'name': 'citas',
            'label': 'Citas',
            'url': 'main.citas',
            'icon': 'bi-calendar-check'
        },
        'consultas': {
            'name': 'consultas',
            'label': 'Consultas',
            'url': 'consultas.index',
            'icon': 'bi-file-medical'
        },
        'emergencias': {
            'name': 'emergencias',
            'label': 'Emergencias',
            'url': 'emergencias.index',
            'icon': 'bi-hospital'
        },
        'internados': {
            'name': 'internados',
            'label': 'Internados',
            'url': 'internados.index',
            'icon': 'bi-building'
        },
        'laboratorio': {
            'name': 'laboratorio',
            'label': 'Laboratorio',
            'url': 'laboratorio.index',
            'icon': 'bi-file-earmark-medical'
        },
        'medicamentos': {
            'name': 'medicamentos',
            'label': 'Medicamentos',
            'url': 'medicamentos.index',
            'icon': 'bi-capsule'
        },
        'especialidades': {
            'name': 'especialidades',
            'label': 'Especialidades',
            'url': 'especialidades.index',
            'icon': 'bi-heart-pulse'
        },
        'enfermeros': {
            'name': 'enfermeros',
            'label': 'Enfermeros',
            'url': 'enfermeros.index',
            'icon': 'bi-clipboard-heart'
        },
        'reportes': {
            'name': 'reportes',
            'label': 'Reportes',
            'url': 'main.reportes',
            'icon': 'bi-graph-up'
        }
    }
    
    # Menú por rol
    MENU_BY_ROLE = {
        'admin': [
            'dashboard', 'pacientes', 'emergencias', 'consultas', 'doctores',
            'citas', 'internados', 'laboratorio', 'medicamentos', 'especialidades', 
            'enfermeros', 'reportes'
        ],
        'medico': [
            'dashboard', 'consultas', 'pacientes', 'citas', 'emergencias', 'laboratorio'
        ],
        'enfermera': [
            'dashboard', 'consultas', 'internados', 'pacientes', 'emergencias'
        ],
        'recepcionista': [
            'dashboard', 'citas', 'pacientes'
        ],
        'farmacia': [
            'dashboard', 'medicamentos'
        ],
        'laboratorio': [
            'dashboard', 'laboratorio'
        ]
    }
    
    # Obtener el rol del usuario (por defecto recepcionista si no está definido)
    user_role = user.rol if user and hasattr(user, 'rol') else 'recepcionista'
    
    # Obtener lista de items permitidos para este rol
    allowed_items = MENU_BY_ROLE.get(user_role, ['dashboard'])
    
    # Construir menú con metadatos completos
    menu = []
    for item_name in allowed_items:
        if item_name in MENU_ITEMS:
            menu.append(MENU_ITEMS[item_name])
    
    return menu


def is_menu_active(menu_item_name, current_endpoint):
    """
    Determina si un item del menú está activo según el endpoint actual
    
    Args:
        menu_item_name: Nombre del item del menú
        current_endpoint: request.endpoint actual
        
    Returns:
        bool: True si el item está activo
    """
    if not current_endpoint:
        return False
    
    # Mapeo de items a prefijos de endpoints
    endpoint_mapping = {
        'dashboard': ['main.dashboard', 'main.index'],
        'doctores': ['main.usuarios'],
        'pacientes': ['main.pacientes', 'main.paciente'],
        'citas': ['main.citas', 'main.cita'],
        'consultas': ['consultas.'],
        'emergencias': ['emergencias.'],
        'internados': ['internados.'],
        'laboratorio': ['laboratorio.'],
        'medicamentos': ['medicamentos.'],
        'especialidades': ['especialidades.'],
        'enfermeros': ['enfermeros.'],
        'reportes': ['main.reportes']
    }
    
    # Verificar si el endpoint actual coincide con algún prefijo del item
    prefixes = endpoint_mapping.get(menu_item_name, [])
    for prefix in prefixes:
        if current_endpoint.startswith(prefix):
            return True
    
    return False
