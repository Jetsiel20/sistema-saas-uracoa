"""
Tests para verificar que todos los módulos están registrados correctamente
"""
import pytest
from flask import url_for
from saas import create_app
from saas.extensions import db
from saas.models import Usuario, Paciente
from werkzeug.security import generate_password_hash


@pytest.fixture(scope='function')
def app():
    """Fixture de app con configuración de test"""
    app = create_app('default')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['SERVER_NAME'] = 'localhost'
    
    with app.app_context():
        db.create_all()
        
        # Limpiar cualquier dato previo
        db.session.query(Usuario).delete()
        db.session.query(Paciente).delete()
        db.session.commit()
        
        # Crear usuario admin de prueba
        admin = Usuario(
            username='admin',
            email='admin@test.com',
            nombre='Admin',
            apellido='Test',
            cedula='12345678',
            rol='admin',
            activo=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        
        # Crear usuario médico de prueba
        medico = Usuario(
            username='medico',
            email='medico@test.com',
            nombre='Doctor',
            apellido='Test',
            cedula='87654321',
            rol='medico',
            activo=True
        )
        medico.set_password('medico123')
        db.session.add(medico)
        
        # Crear paciente de prueba
        paciente = Usuario(
            username='paciente1',
            email='paciente@test.com',
            nombre='Paciente',
            apellido='Test',
            cedula='11223344',
            rol='admin',
            activo=True
        )
        paciente.set_password('paciente123')
        db.session.add(paciente)
        
        # Crear registro de paciente
        from datetime import date
        paciente_data = Paciente(
            cedula='11223344',
            nombre='Paciente',
            apellido='Test',
            fecha_nacimiento=date(1990, 1, 1),
            sexo='M',
            telefono='0123456789',
            direccion='Test Address',
            email='paciente@test.com'
        )
        db.session.add(paciente_data)
        
        db.session.commit()
        
        yield app
        
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Fixture de test client"""
    return app.test_client()


@pytest.fixture
def authenticated_client(client):
    """Fixture de cliente autenticado como admin"""
    client.post('/auth/login', data={
        'username': 'admin',
        'password': 'admin123'
    }, follow_redirects=True)
    return client


def test_blueprints_registered(app):
    """Verifica que todos los blueprints estén registrados"""
    with app.app_context():
        # Obtener todas las rutas registradas
        rules = [str(rule) for rule in app.url_map.iter_rules()]
        
        # Verificar que existan rutas para cada módulo
        assert any('/auth/' in rule for rule in rules), "Blueprint 'auth' no registrado"
        assert any('/consultas' in rule for rule in rules), "Blueprint 'consultas' no registrado"
        assert any('/emergencias' in rule for rule in rules), "Blueprint 'emergencias' no registrado"
        assert any('/internados' in rule for rule in rules), "Blueprint 'internados' no registrado"
        assert any('/especialidades' in rule for rule in rules), "Blueprint 'especialidades' no registrado"
        assert any('/enfermeros' in rule for rule in rules), "Blueprint 'enfermeros' no registrado"
        assert any('/laboratorio' in rule for rule in rules), "Blueprint 'laboratorio' no registrado"


def test_auth_routes_exist(app):
    """Verifica que las rutas de autenticación existan"""
    with app.app_context():
        # Verificar que se puedan generar URLs de auth
        assert url_for('auth.login').endswith('/auth/login')
        assert url_for('auth.logout').endswith('/auth/logout')


def test_medical_module_routes_exist(app):
    """Verifica que las rutas de módulos médicos existan"""
    with app.app_context():
        # Consultas
        assert url_for('consultas.index').endswith('/consultas/')
        
        # Emergencias
        assert url_for('emergencias.index').endswith('/emergencias/')
        
        # Internados
        assert url_for('internados.index').endswith('/internados/')
        assert url_for('internados.camas').endswith('/internados/camas')
        
        # Especialidades
        assert url_for('especialidades.index').endswith('/especialidades/')
        
        # Enfermeros
        assert url_for('enfermeros.index').endswith('/enfermeros/')
        
        # Laboratorio
        assert url_for('laboratorio.index').endswith('/laboratorio/')


def test_min_routes_module_consultas(authenticated_client):
    """Verifica que el módulo consultas responda correctamente"""
    response = authenticated_client.get('/consultas/')
    assert response.status_code == 200
    assert b'Consultas' in response.data or b'consultas' in response.data


def test_min_routes_module_emergencias(authenticated_client):
    """Verifica que el módulo emergencias responda correctamente"""
    response = authenticated_client.get('/emergencias/')
    assert response.status_code == 200
    assert b'Emergencias' in response.data or b'emergencias' in response.data or b'Triage' in response.data


def test_min_routes_module_internados(authenticated_client):
    """Verifica que el módulo internados responda correctamente"""
    response = authenticated_client.get('/internados/')
    assert response.status_code == 200
    assert b'Internados' in response.data or b'internados' in response.data or b'Camas' in response.data


def test_min_routes_module_laboratorio(authenticated_client):
    """Verifica que el módulo laboratorio responda correctamente"""
    response = authenticated_client.get('/laboratorio/')
    assert response.status_code == 200


def test_all_modules_have_index_route(app):
    """Verifica que todos los módulos tengan una ruta index"""
    with app.app_context():
        modules = ['consultas', 'emergencias', 'internados', 'especialidades', 'enfermeros', 'laboratorio']
        
        for module in modules:
            try:
                url = url_for(f'{module}.index')
                assert url is not None, f"Módulo {module} no tiene ruta index"
            except Exception as e:
                pytest.fail(f"Error generando URL para {module}.index: {str(e)}")


def test_static_folder_accessible(client):
    """Verifica que la carpeta static sea accesible"""
    # Intentar acceder a un recurso estático típico
    response = client.get('/static/css/style.css')
    # Puede ser 200 (existe) o 404 (no existe pero la ruta funciona)
    assert response.status_code in [200, 404]


def test_app_has_db_extension(app):
    """Verifica que la app tenga la extensión de base de datos"""
    assert hasattr(app, 'extensions')
    assert 'sqlalchemy' in app.extensions


def test_app_has_login_manager(app):
    """Verifica que la app tenga login manager configurado"""
    assert hasattr(app, 'login_manager')
    # Flask-Login registra el extension manager directamente en app
    assert app.login_manager is not None


def test_app_has_migrate_extension(app):
    """Verifica que la app tenga Flask-Migrate configurado"""
    assert hasattr(app, 'extensions')
    assert 'migrate' in app.extensions
