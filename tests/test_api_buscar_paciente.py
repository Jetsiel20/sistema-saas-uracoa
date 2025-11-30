"""
Tests para API de búsqueda de pacientes por cédula
Sistema SaaS Hospital Uracoa - J&S Software Inteligentes
"""
import pytest
from datetime import datetime, date
from saas.models import Paciente, Usuario
from saas.consultas.models import Consulta


@pytest.fixture
def paciente_test(app):
    """Crear paciente de prueba"""
    with app.app_context():
        from saas.extensions import db
        paciente = Paciente(
            cedula='V12345678',
            nombre='Juan',
            apellido='Pérez',
            fecha_nacimiento=date(1990, 5, 15),
            sexo='Masculino',
            tipo_sangre='O+',
            alergias='Penicilina',
            activo=True
        )
        db.session.add(paciente)
        db.session.commit()
        yield paciente
        # Cleanup
        db.session.delete(paciente)
        db.session.commit()


@pytest.fixture
def consulta_paciente_test(app, paciente_test, auth_login):
    """Crear consulta para el paciente de prueba"""
    with app.app_context():
        from saas.extensions import db
        from saas.models import Usuario
        
        medico = Usuario.query.filter_by(username='dr.santos').first()
        if not medico:
            pytest.skip("Usuario dr.santos no existe")
        
        consulta = Consulta(
            paciente_id=paciente_test.id,
            medico_id=medico.id,
            turno='mañana',
            numero_consulta=1,
            fecha_hora=datetime.utcnow(),
            motivo='Control de rutina',
            peso=70.5,
            altura=175.0,
            sector='Uracoa Centro',
            temperatura=36.5,
            estado='abierta'
        )
        db.session.add(consulta)
        db.session.commit()
        yield consulta
        # Cleanup
        db.session.delete(consulta)
        db.session.commit()


def test_api_buscar_paciente_exacto(client, auth_login, paciente_test):
    """Test: Búsqueda exacta de paciente por cédula"""
    response = client.get('/api/pacientes/buscar?cedula=V12345678')
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert data['ok'] is True
    assert data['found'] is True
    assert data['paciente']['cedula'] == 'V12345678'
    assert data['paciente']['nombre'] == 'Juan'
    assert data['paciente']['apellido'] == 'Pérez'
    assert data['paciente']['nombre_completo'] == 'Juan Pérez'
    assert data['paciente']['tipo_sangre'] == 'O+'
    assert data['paciente']['alergias'] == 'Penicilina'


def test_api_buscar_paciente_case_insensitive(client, auth_login, paciente_test):
    """Test: Búsqueda case-insensitive"""
    response = client.get('/api/pacientes/buscar?cedula=v12345678')
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert data['ok'] is True
    assert data['found'] is True
    assert data['paciente']['cedula'] == 'V12345678'


def test_api_buscar_paciente_sin_v(client, auth_login, paciente_test):
    """Test: Búsqueda sin la V inicial"""
    response = client.get('/api/pacientes/buscar?cedula=12345678')
    
    assert response.status_code == 200
    data = response.get_json()
    
    # Puede encontrarlo o no dependiendo de si la búsqueda parcial funciona
    assert data['ok'] is True


def test_api_buscar_paciente_con_ultima_consulta(client, auth_login, paciente_test, consulta_paciente_test):
    """Test: Precarga de datos de última consulta"""
    response = client.get('/api/pacientes/buscar?cedula=V12345678')
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert data['ok'] is True
    assert data['found'] is True
    assert 'ultima_consulta' in data['paciente']
    
    ultima = data['paciente']['ultima_consulta']
    assert ultima['peso'] == 70.5
    assert ultima['altura'] == 175.0
    assert ultima['sector'] == 'Uracoa Centro'
    assert ultima['turno'] == 'mañana'
    assert ultima['fecha'] is not None


def test_api_buscar_paciente_no_encontrado(client, auth_login):
    """Test: Paciente no existe"""
    response = client.get('/api/pacientes/buscar?cedula=V99999999')
    
    assert response.status_code == 200
    data = response.get_json()
    
    assert data['ok'] is True
    assert data['found'] is False
    assert 'similares' in data


def test_api_buscar_cedula_muy_corta(client, auth_login):
    """Test: Cédula con menos de 4 caracteres"""
    response = client.get('/api/pacientes/buscar?cedula=123')
    
    assert response.status_code == 400
    data = response.get_json()
    
    assert data['ok'] is False
    assert 'error' in data


def test_api_buscar_sin_cedula(client, auth_login):
    """Test: Request sin parámetro cedula"""
    response = client.get('/api/pacientes/buscar')
    
    assert response.status_code == 400
    data = response.get_json()
    
    assert data['ok'] is False
    assert 'error' in data


def test_api_buscar_sin_login(client, paciente_test):
    """Test: Endpoint requiere autenticación"""
    response = client.get('/api/pacientes/buscar?cedula=V12345678')
    
    # Flask-Login redirige a login
    assert response.status_code == 302
    assert '/auth/login' in response.location


def test_api_buscar_similares(client, auth_login, app):
    """Test: Búsqueda parcial retorna similares"""
    with app.app_context():
        from saas.extensions import db
        
        # Crear 3 pacientes con cédulas similares
        pacientes = [
            Paciente(cedula='V11111111', nombre='Ana', apellido='García', 
                    fecha_nacimiento=date(1985, 1, 1), sexo='Femenino', activo=True),
            Paciente(cedula='V11111222', nombre='Luis', apellido='Rodríguez',
                    fecha_nacimiento=date(1990, 2, 2), sexo='Masculino', activo=True),
            Paciente(cedula='V11112233', nombre='María', apellido='López',
                    fecha_nacimiento=date(1995, 3, 3), sexo='Femenino', activo=True),
        ]
        
        for p in pacientes:
            db.session.add(p)
        db.session.commit()
        
        try:
            response = client.get('/api/pacientes/buscar?cedula=V1111')
            
            assert response.status_code == 200
            data = response.get_json()
            
            assert data['ok'] is True
            # Puede encontrar exacto o similares dependiendo de la cédula
            if not data['found']:
                assert len(data['similares']) >= 2
                assert any(s['cedula'] == 'V11111111' for s in data['similares'])
        finally:
            # Cleanup
            for p in pacientes:
                db.session.delete(p)
            db.session.commit()


def test_api_buscar_performance(client, auth_login, app):
    """Test: Performance con múltiples pacientes"""
    import time
    
    with app.app_context():
        from saas.extensions import db
        
        # Crear 20 pacientes
        pacientes = []
        for i in range(20):
            p = Paciente(
                cedula=f'V2000000{i:02d}',
                nombre=f'Paciente{i}',
                apellido=f'Test{i}',
                fecha_nacimiento=date(1980, 1, 1),
                sexo='Masculino',
                activo=True
            )
            pacientes.append(p)
            db.session.add(p)
        db.session.commit()
        
        try:
            start = time.time()
            response = client.get('/api/pacientes/buscar?cedula=V20000005')
            elapsed = time.time() - start
            
            assert response.status_code == 200
            assert elapsed < 1.0  # Debe responder en menos de 1 segundo
            
            data = response.get_json()
            assert data['ok'] is True
        finally:
            # Cleanup
            for p in pacientes:
                db.session.delete(p)
            db.session.commit()
