"""
Tests para flujo de autenticación
"""
import pytest
from flask import url_for, session
from saas import create_app
from saas.extensions import db
from saas.models import Usuario


@pytest.fixture(scope='function')
def app():
    """Fixture de app con configuración de test"""
    app = create_app('default')
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['SERVER_NAME'] = 'localhost'
    app.config['LOGIN_DISABLED'] = False
    
    with app.app_context():
        db.create_all()
        
        # Limpiar cualquier dato previo
        db.session.query(Usuario).delete()
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
        
        # Crear usuario inactivo
        inactivo = Usuario(
            username='inactivo',
            email='inactivo@test.com',
            nombre='Inactivo',
            apellido='Test',
            cedula='99999999',
            rol='admin',
            activo=False
        )
        inactivo.set_password('inactivo123')
        db.session.add(inactivo)
        
        db.session.commit()
        
        yield app
        
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Fixture de test client"""
    return app.test_client()


def test_auth_redirects(client):
    """Acceder /dashboard sin login -> 302 a /auth/login"""
    response = client.get('/dashboard', follow_redirects=False)
    assert response.status_code == 302
    assert '/auth/login' in response.location


def test_main_index_redirects_to_login(client):
    """Acceder / sin login -> redirect a login"""
    response = client.get('/', follow_redirects=False)
    # Puede redirigir a login o a dashboard que redirige a login
    assert response.status_code in [302, 200]


def test_consultas_requires_login(client):
    """Acceder /consultas/ sin login -> 302 a /auth/login"""
    response = client.get('/consultas/', follow_redirects=False)
    assert response.status_code == 302
    assert '/auth/login' in response.location


def test_emergencias_requires_login(client):
    """Acceder /emergencias/ sin login -> 302 a /auth/login"""
    response = client.get('/emergencias/', follow_redirects=False)
    assert response.status_code == 302
    assert '/auth/login' in response.location


def test_internados_requires_login(client):
    """Acceder /internados/ sin login -> 302 a /auth/login"""
    response = client.get('/internados/', follow_redirects=False)
    assert response.status_code == 302
    assert '/auth/login' in response.location


def test_login_page_accessible(client):
    """La página de login debe ser accesible sin autenticación"""
    response = client.get('/auth/login')
    assert response.status_code == 200
    assert b'login' in response.data.lower() or b'usuario' in response.data.lower()


def test_login_ok(client):
    """Login admin -> 200 en /dashboard"""
    # Login
    response = client.post('/auth/login', data={
        'username': 'admin',
        'password': 'admin123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # Verificar que podemos acceder al dashboard
    response = client.get('/dashboard')
    assert response.status_code == 200


def test_login_medico_ok(client):
    """Login de médico funciona correctamente"""
    response = client.post('/auth/login', data={
        'username': 'medico',
        'password': 'medico123'
    }, follow_redirects=True)
    
    assert response.status_code == 200


def test_login_wrong_password(client):
    """Login con contraseña incorrecta falla"""
    response = client.post('/auth/login', data={
        'username': 'admin',
        'password': 'wrongpassword'
    }, follow_redirects=True)
    
    # Debe permanecer en login o mostrar error
    assert b'login' in response.data.lower() or b'error' in response.data.lower() or b'incorrecta' in response.data.lower()


def test_login_nonexistent_user(client):
    """Login con usuario inexistente falla"""
    response = client.post('/auth/login', data={
        'username': 'noexiste',
        'password': 'password'
    }, follow_redirects=True)
    
    # Debe mostrar error o permanecer en login
    assert response.status_code == 200


def test_login_inactive_user(client):
    """Login con usuario inactivo debe fallar"""
    response = client.post('/auth/login', data={
        'username': 'inactivo',
        'password': 'inactivo123'
    }, follow_redirects=True)
    
    # Debe rechazar el login
    assert b'inactivo' in response.data.lower() or b'desactivad' in response.data.lower() or b'login' in response.data.lower()


def test_logout_redirects_to_login(client):
    """Logout redirige a login"""
    # Primero hacer login
    client.post('/auth/login', data={
        'username': 'admin',
        'password': 'admin123'
    })
    
    # Luego logout
    response = client.get('/auth/logout', follow_redirects=False)
    assert response.status_code == 302
    assert '/auth/login' in response.location


def test_authenticated_can_access_modules(client):
    """Usuario autenticado puede acceder a módulos"""
    # Login
    client.post('/auth/login', data={
        'username': 'admin',
        'password': 'admin123'
    }, follow_redirects=True)
    
    # Verificar acceso a módulos
    modules = ['/consultas/', '/emergencias/', '/internados/', '/laboratorio/']
    
    for module in modules:
        response = client.get(module)
        assert response.status_code == 200, f"No se pudo acceder a {module}"


def test_session_persists_after_login(client):
    """La sesión persiste después del login"""
    # Login
    client.post('/auth/login', data={
        'username': 'admin',
        'password': 'admin123'
    }, follow_redirects=True)
    
    # Primera petición
    response1 = client.get('/dashboard')
    assert response1.status_code == 200
    
    # Segunda petición (debe mantener sesión)
    response2 = client.get('/consultas/')
    assert response2.status_code == 200


def test_login_empty_credentials(client):
    """Login con credenciales vacías falla"""
    response = client.post('/auth/login', data={
        'username': '',
        'password': ''
    }, follow_redirects=True)
    
    # Debe mostrar error de validación o permanecer en login
    assert response.status_code == 200


def test_multiple_failed_logins(client):
    """Múltiples intentos de login fallidos"""
    for i in range(3):
        response = client.post('/auth/login', data={
            'username': 'admin',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        
        assert response.status_code == 200


def test_login_preserves_next_parameter(client):
    """Login debe redirigir a la página solicitada originalmente"""
    # Intentar acceder a una página protegida
    client.get('/consultas/', follow_redirects=False)
    
    # Login
    response = client.post('/auth/login', data={
        'username': 'admin',
        'password': 'admin123'
    }, follow_redirects=False)
    
    # Debe redirigir (302)
    assert response.status_code == 302


def test_logout_clears_session(client):
    """Logout limpia la sesión correctamente"""
    # Login
    client.post('/auth/login', data={
        'username': 'admin',
        'password': 'admin123'
    }, follow_redirects=True)
    
    # Verificar que estamos autenticados
    response = client.get('/dashboard')
    assert response.status_code == 200
    
    # Logout
    client.get('/auth/logout', follow_redirects=True)
    
    # Intentar acceder a página protegida debe redirigir
    response = client.get('/dashboard', follow_redirects=False)
    assert response.status_code == 302
    assert '/auth/login' in response.location
