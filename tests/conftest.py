"""
Configuración de fixtures compartidas para tests
"""
import pytest
from flask import url_for
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
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture(scope='function')
def db_session(app):
    """Fixture de sesión de base de datos"""
    with app.app_context():
        yield db.session


@pytest.fixture(scope='function')
def client(app):
    """Fixture de test client"""
    return app.test_client()


@pytest.fixture(scope='function')
def auth_login(client, app):
    """Fixture para login automático en tests"""
    # Crear usuario de prueba dentro del contexto de la app
    usuario = Usuario(
        username='test_user',
        email='test@hospital.com',
        nombre='Test',
        apellido='User',
        rol='medico',
        activo=True
    )
    usuario.set_password('testpass123')
    db.session.add(usuario)
    db.session.commit()
    
    # Login
    client.post('/auth/login', data={
        'username': 'test_user',
        'password': 'testpass123'
    }, follow_redirects=True)
    
    yield usuario
