"""
Tests para el sistema de turnos de consultas.
Valida la lógica de límite de 20 consultas por turno y asignación automática.
"""
import pytest
from datetime import datetime, time, date
from unittest.mock import patch, MagicMock
from saas.consultas.models import Consulta
from saas.models import Usuario, Paciente
from saas.extensions import db


class TestDeteccionTurno:
    """Tests para detectar_turno_actual()"""
    
    @patch('saas.consultas.models.datetime')
    def test_turno_manana_inicio(self, mock_datetime):
        """Debe detectar turno mañana a las 07:00"""
        mock_datetime.utcnow.return_value = datetime(2024, 1, 15, 7, 0)
        mock_datetime.hour = datetime(2024, 1, 15, 7, 0).hour
        
        # Simular que .hour devuelve 7
        mock_now = MagicMock()
        mock_now.hour = 7
        mock_datetime.utcnow.return_value = mock_now
        
        turno = Consulta.detectar_turno_actual()
        assert turno == 'mañana'
    
    @patch('saas.consultas.models.datetime')
    def test_turno_manana_fin(self, mock_datetime):
        """Debe detectar turno mañana a las 12:59"""
        mock_now = MagicMock()
        mock_now.hour = 12
        mock_datetime.utcnow.return_value = mock_now
        
        turno = Consulta.detectar_turno_actual()
        assert turno == 'mañana'
    
    @patch('saas.consultas.models.datetime')
    def test_turno_tarde_inicio(self, mock_datetime):
        """Debe detectar turno tarde a las 13:00"""
        mock_now = MagicMock()
        mock_now.hour = 13
        mock_datetime.utcnow.return_value = mock_now
        
        turno = Consulta.detectar_turno_actual()
        assert turno == 'tarde'
    
    @patch('saas.consultas.models.datetime')
    def test_turno_tarde_fin(self, mock_datetime):
        """Debe detectar turno tarde a las 17:59"""
        mock_now = MagicMock()
        mock_now.hour = 17
        mock_datetime.utcnow.return_value = mock_now
        
        turno = Consulta.detectar_turno_actual()
        assert turno == 'tarde'
    
    @patch('saas.consultas.models.datetime')
    def test_fuera_horario_temprano(self, mock_datetime):
        """Debe rechazar registro a las 06:00"""
        mock_now = MagicMock()
        mock_now.hour = 6
        mock_datetime.utcnow.return_value = mock_now
        
        with pytest.raises(ValueError) as excinfo:
            Consulta.detectar_turno_actual()
        
        assert "Fuera del horario" in str(excinfo.value)
    
    @patch('saas.consultas.models.datetime')
    def test_fuera_horario_noche(self, mock_datetime):
        """Debe rechazar registro a las 18:00"""
        mock_now = MagicMock()
        mock_now.hour = 18
        mock_datetime.utcnow.return_value = mock_now
        
        with pytest.raises(ValueError) as excinfo:
            Consulta.detectar_turno_actual()
        
        assert "Fuera del horario" in str(excinfo.value)


class TestLimiteTurnos:
    """Tests para el límite de 20 consultas por turno"""
    
    def test_verificar_disponibilidad_vacio(self, app):
        """Debe mostrar 0/20 en turno vacío"""
        with app.app_context():
            disponible, count, limite = Consulta.verificar_disponibilidad_turno('mañana')
            
            assert disponible is True
            assert count == 0
            assert limite == 20
    
    def test_verificar_disponibilidad_parcial(self, app, db_session):
        """Debe mostrar 10/20 con 10 consultas registradas"""
        with app.app_context():
            # Crear médico y paciente
            medico = Usuario(
                nombre='Dr. Test',
                apellido='Médico',
                email='medico@test.com',
                rol='medico',
                activo=True
            )
            medico.set_password('password')
            db_session.add(medico)
            
            paciente = Paciente(
                nombre='Paciente',
                apellido='Test',
                cedula='1234567890',
                fecha_nacimiento=date(1990, 1, 1),
                sexo='M',
                activo=True
            )
            db_session.add(paciente)
            db_session.commit()
            
            # Crear 10 consultas en turno mañana
            for i in range(10):
                consulta = Consulta(
                    paciente_id=paciente.id,
                    medico_id=medico.id,
                    fecha_hora=datetime.utcnow(),
                    motivo=f'Consulta {i+1}',
                    temperatura=36.5,
                    estado='abierta',
                    turno='mañana',
                    numero_consulta=i+1
                )
                db_session.add(consulta)
            
            db_session.commit()
            
            disponible, count, limite = Consulta.verificar_disponibilidad_turno('mañana')
            
            assert disponible is True
            assert count == 10
            assert limite == 20
    
    def test_verificar_disponibilidad_completo(self, app, db_session):
        """Debe rechazar cuando hay 20/20 consultas"""
        with app.app_context():
            # Crear médico y paciente
            medico = Usuario(
                nombre='Dr. Test',
                apellido='Médico',
                email='medico2@test.com',
                rol='medico',
                activo=True
            )
            medico.set_password('password')
            db_session.add(medico)
            
            paciente = Paciente(
                nombre='Paciente',
                apellido='Test 2',
                cedula='9876543210',
                fecha_nacimiento=date(1990, 1, 1),
                sexo='F',
                activo=True
            )
            db_session.add(paciente)
            db_session.commit()
            
            # Crear 20 consultas en turno tarde
            for i in range(20):
                consulta = Consulta(
                    paciente_id=paciente.id,
                    medico_id=medico.id,
                    fecha_hora=datetime.utcnow(),
                    motivo=f'Consulta {i+1}',
                    temperatura=36.5,
                    estado='abierta',
                    turno='tarde',
                    numero_consulta=i+1
                )
                db_session.add(consulta)
            
            db_session.commit()
            
            disponible, count, limite = Consulta.verificar_disponibilidad_turno('tarde')
            
            assert disponible is False
            assert count == 20
            assert limite == 20


class TestAsignacionTurnoNumero:
    """Tests para asignar_turno_y_numero()"""
    
    @patch('saas.consultas.models.Consulta.detectar_turno_actual')
    @patch('saas.consultas.models.Consulta.verificar_disponibilidad_turno')
    def test_asignar_primera_consulta(self, mock_verificar, mock_detectar, app, db_session):
        """Primera consulta debe ser #1"""
        mock_detectar.return_value = 'mañana'
        mock_verificar.return_value = (True, 0, 20)  # disponible, 0 consultas, límite 20
        
        with app.app_context():
            # Crear médico y paciente
            medico = Usuario(
                nombre='Dr. Test',
                apellido='Asignación',
                email='asignacion@test.com',
                rol='medico',
                activo=True
            )
            medico.set_password('password')
            db_session.add(medico)
            
            paciente = Paciente(
                nombre='Paciente',
                apellido='Turno',
                cedula='1111111111',
                fecha_nacimiento=date(1990, 1, 1),
                sexo='M',
                activo=True
            )
            db_session.add(paciente)
            db_session.commit()
            
            consulta = Consulta(
                paciente_id=paciente.id,
                medico_id=medico.id,
                fecha_hora=datetime.utcnow(),
                motivo='Primera consulta del día',
                temperatura=36.5,
                estado='abierta'
            )
            
            consulta.asignar_turno_y_numero()
            
            assert consulta.turno == 'mañana'
            assert consulta.numero_consulta == 1
    
    @patch('saas.consultas.models.Consulta.detectar_turno_actual')
    @patch('saas.consultas.models.Consulta.verificar_disponibilidad_turno')
    def test_asignar_consulta_21_rechaza(self, mock_verificar, mock_detectar):
        """Consulta #21 debe ser rechazada"""
        mock_detectar.return_value = 'tarde'
        mock_verificar.return_value = (False, 20, 20)  # NO disponible, 20 consultas, límite 20
        
        consulta = Consulta(
            paciente_id=1,
            medico_id=1,
            fecha_hora=datetime.utcnow(),
            motivo='Intento de consulta 21',
            temperatura=36.5,
            estado='abierta'
        )
        
        with pytest.raises(ValueError) as excinfo:
            consulta.asignar_turno_y_numero()
        
        # Verificar que el mensaje de error contiene información del límite
        error_msg = str(excinfo.value)
        assert "20 consultas" in error_msg
        assert "tarde" in error_msg


class TestIntegracionTurnos:
    """Tests de integración completa del sistema de turnos"""
    
    @patch('saas.consultas.models.datetime')
    def test_flujo_completo_20_consultas(self, mock_datetime, app, db_session):
        """Debe permitir 20 consultas y rechazar la 21"""
        # Simular que estamos en horario de mañana (10:00)
        mock_now = MagicMock()
        mock_now.hour = 10
        mock_datetime.utcnow.return_value = mock_now
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs) if args else mock_now
        
        with app.app_context():
            # Crear médico y paciente
            medico = Usuario(
                nombre='Dr. Integración',
                apellido='Test',
                email='integracion@test.com',
                rol='medico',
                activo=True
            )
            medico.set_password('password')
            db_session.add(medico)
            
            paciente = Paciente(
                nombre='Paciente',
                apellido='Límite',
                cedula='2222222222',
                fecha_nacimiento=date(1985, 5, 15),
                sexo='F',
                activo=True
            )
            db_session.add(paciente)
            db_session.commit()
            
            # Crear 20 consultas exitosamente
            for i in range(20):
                consulta = Consulta(
                    paciente_id=paciente.id,
                    medico_id=medico.id,
                    fecha_hora=datetime.utcnow(),
                    motivo=f'Consulta límite {i+1}',
                    temperatura=36.5,
                    estado='abierta'
                )
                
                consulta.asignar_turno_y_numero()
                assert consulta.turno == 'mañana'
                assert consulta.numero_consulta == i + 1
                
                db_session.add(consulta)
                db_session.commit()
            
            # Verificar que hay exactamente 20
            count = Consulta.query.filter_by(turno='mañana').count()
            assert count == 20
            
            # Intentar crear la consulta #21 debe fallar
            consulta_21 = Consulta(
                paciente_id=paciente.id,
                medico_id=medico.id,
                fecha_hora=datetime.utcnow(),
                motivo='Esta debe ser rechazada',
                temperatura=36.5,
                estado='abierta'
            )
            
            with pytest.raises(ValueError) as excinfo:
                consulta_21.asignar_turno_y_numero()
            
            assert "Límite de 20 consultas alcanzado" in str(excinfo.value)


class TestAlertasClinicas:
    """Tests para el sistema de alertas clínicas automáticas"""
    
    def test_alerta_fiebre(self, app):
        """Debe detectar fiebre >= 38°C"""
        with app.app_context():
            consulta = Consulta(
                temperatura=38.5,
                estado='abierta',
                motivo='Test fiebre'
            )
            
            alertas = consulta.alertas_detalle
            assert any('fiebre' in a.lower() for a in alertas)
    
    def test_alerta_hipoxemia(self, app):
        """Debe detectar saturación < 92%"""
        with app.app_context():
            consulta = Consulta(
                saturacion=90,
                estado='abierta',
                motivo='Test hipoxemia'
            )
            
            alertas = consulta.alertas_detalle
            assert any('hipoxemia' in a.lower() or 'saturación' in a.lower() for a in alertas)
    
    def test_alerta_hipertension(self, app):
        """Debe detectar presión >= 140/90"""
        with app.app_context():
            consulta = Consulta(
                presion_sistolica=150,
                presion_diastolica=95,
                estado='abierta',
                motivo='Test hipertensión'
            )
            
            alertas = consulta.alertas_detalle
            assert any('hipertensión' in a.lower() or 'presión' in a.lower() for a in alertas)
    
    def test_alerta_obesidad(self, app):
        """Debe detectar IMC > 30"""
        with app.app_context():
            consulta = Consulta(
                peso=100,
                altura=170,
                estado='abierta',
                motivo='Test obesidad'
            )
            
            # IMC = 100 / (1.7^2) = 34.6
            assert consulta.imc > 30
            alertas = consulta.alertas_detalle
            assert any('obesidad' in a.lower() or 'imc' in a.lower() for a in alertas)
    
    def test_sin_alertas(self, app):
        """Consulta normal no debe generar alertas"""
        with app.app_context():
            consulta = Consulta(
                temperatura=36.5,
                presion_sistolica=120,
                presion_diastolica=80,
                saturacion=98,
                peso=70,
                altura=170,
                estado='abierta',
                motivo='Consulta normal'
            )
            
            alertas = consulta.alertas_detalle
            assert len(alertas) == 0
