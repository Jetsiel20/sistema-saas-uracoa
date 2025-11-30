from datetime import datetime
from saas.extensions import db
from sqlalchemy import func

class Consulta(db.Model):
    """
    Modelo para consultas médicas diarias con signos vitales completos.
    Sistema de turnos: máximo 20 consultas por turno (mañana/tarde).
    """
    __tablename__ = 'consultas'
    
    # Identificadores
    id = db.Column(db.Integer, primary_key=True)
    
    # Control de turnos (J&S Software Inteligentes)
    turno = db.Column(db.String(20), default='mañana', nullable=False, index=True)  # 'mañana' o 'tarde'
    numero_consulta = db.Column(db.Integer, nullable=False)  # Consecutivo diario por turno (1-20)
    
    # Relaciones
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False, index=True)
    medico_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, index=True)
    cita_id = db.Column(db.Integer, db.ForeignKey('citas.id'), nullable=True)
    
    # Fecha y hora de la consulta
    fecha_hora = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Signos vitales completos
    temperatura = db.Column(db.Float)  # °C
    presion_sistolica = db.Column(db.Integer)  # mmHg
    presion_diastolica = db.Column(db.Integer)  # mmHg
    frecuencia_cardiaca = db.Column(db.Integer)  # BPM
    saturacion = db.Column(db.Integer)  # SpO2 %
    peso = db.Column(db.Float)  # kg
    altura = db.Column(db.Float)  # cm
    
    # Motivo, diagnóstico y tratamiento
    motivo = db.Column(db.Text, nullable=False)
    diagnostico = db.Column(db.Text)
    tratamiento = db.Column(db.Text)
    observaciones = db.Column(db.Text)
    
    # Datos contextuales rurales
    sector = db.Column(db.String(120), nullable=True, index=True)  # Sector o comunidad rural
    nivel_conciencia = db.Column(db.String(50), nullable=True)  # Alerta, Somnoliento, Inconsciente
    
    # Estado
    estado = db.Column(db.String(20), default='abierta', nullable=False, index=True)  # abierta, cerrada
    fecha_cierre = db.Column(db.DateTime, nullable=True)  # Fecha de cierre de consulta
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    paciente = db.relationship('Paciente', backref='consultas_realizadas')
    medico = db.relationship('Usuario', backref='consultas_realizadas', foreign_keys=[medico_id])
    cita = db.relationship('Cita', backref='consulta_asociada', foreign_keys=[cita_id])
    
    def __repr__(self):
        return f'<Consulta #{self.numero_consulta} - Turno {self.turno} - Paciente {self.paciente_id}>'
    
    @staticmethod
    def detectar_turno_actual():
        """
        Detecta el turno según la hora actual de Venezuela (UTC-4).
        Mañana: 07:00 - 12:00
        Tarde: 13:30 - 17:00
        """
        from datetime import timezone, timedelta
        # Hora de Venezuela (UTC-4)
        tz_venezuela = timezone(timedelta(hours=-4))
        hora_actual = datetime.now(tz_venezuela).hour
        minuto_actual = datetime.now(tz_venezuela).minute
        
        # Mañana: 07:00 - 12:00
        if 7 <= hora_actual < 12:
            return 'mañana'
        elif hora_actual == 12 and minuto_actual == 0:
            return 'mañana'
        # Tarde: 13:30 - 17:00
        elif (hora_actual == 13 and minuto_actual >= 30) or (14 <= hora_actual < 17):
            return 'tarde'
        elif hora_actual == 17 and minuto_actual == 0:
            return 'tarde'
        else:
            raise ValueError("Fuera del horario de atención. Horarios: Mañana (07:00-12:00), Tarde (13:30-17:00)")
    
    @staticmethod
    def contar_consultas_turno(turno, fecha=None):
        """
        Cuenta cuántas consultas hay en un turno específico de una fecha.
        Retorna el número de consultas existentes.
        """
        if fecha is None:
            from datetime import timezone, timedelta
            # Hora de Venezuela (UTC-4)
            tz_venezuela = timezone(timedelta(hours=-4))
            fecha = datetime.now(tz_venezuela).date()
        
        return Consulta.query.filter(
            func.date(Consulta.fecha_hora) == fecha,
            Consulta.turno == turno
        ).count()
    
    @staticmethod
    def verificar_disponibilidad_turno(turno=None):
        """
        Verifica si hay espacio disponible en el turno.
        Retorna: (disponible: bool, consultas_actuales: int, limite: int)
        """
        LIMITE_POR_TURNO = 20
        
        if turno is None:
            turno = Consulta.detectar_turno_actual()
        
        consultas_actuales = Consulta.contar_consultas_turno(turno)
        disponible = consultas_actuales < LIMITE_POR_TURNO
        
        return disponible, consultas_actuales, LIMITE_POR_TURNO
    
    def asignar_turno_y_numero(self):
        """
        Asigna automáticamente el turno y número correlativo.
        Debe llamarse ANTES de db.session.add()
        """
        # Detectar turno según hora
        self.turno = Consulta.detectar_turno_actual()
        
        # Verificar disponibilidad
        disponible, consultas_actuales, limite = Consulta.verificar_disponibilidad_turno(self.turno)
        
        if not disponible:
            raise ValueError(
                f"❌ Límite de {limite} consultas para el turno de {self.turno} ya fue alcanzado. "
                f"Actualmente hay {consultas_actuales} consultas registradas."
            )
        
        # Asignar número correlativo (siguiente disponible)
        self.numero_consulta = consultas_actuales + 1
    
    def validar_antes_guardar(self):
        """Validaciones clínicas antes de guardar en base de datos"""
        if self.presion_diastolica and self.presion_sistolica:
            if self.presion_diastolica >= self.presion_sistolica:
                raise ValueError("La presión diastólica debe ser menor que la sistólica")
        
        if self.peso and self.altura:
            altura_metros = self.altura / 100
            imc = self.peso / (altura_metros ** 2)
            if imc < 10 or imc > 80:
                raise ValueError("IMC fuera de rango razonable (10-80)")
    
    @property
    def imc(self):
        """Calcula el Índice de Masa Corporal (IMC)"""
        if self.peso and self.altura and self.altura > 0:
            altura_metros = self.altura / 100
            return round(self.peso / (altura_metros ** 2), 2)
        return None
    
    @property
    def alerta_riesgo(self):
        """Determina si hay alertas de riesgo según signos vitales"""
        if self.temperatura and self.temperatura >= 38:
            return True
        if self.presion_sistolica and self.presion_sistolica >= 140:
            return True
        if self.presion_diastolica and self.presion_diastolica >= 90:
            return True
        if self.imc and self.imc > 30:
            return True
        return False
    
    @property
    def alertas_detalle(self):
        """Retorna lista de alertas específicas con tipo y mensaje"""
        alertas = []
        
        if self.temperatura and self.temperatura >= 38:
            alertas.append({
                'tipo': 'fiebre',
                'mensaje': f'Fiebre: {self.temperatura}°C',
                'clase': 'danger',
                'icono': 'thermometer-high'
            })
        
        if self.presion_sistolica and self.presion_sistolica >= 140:
            alertas.append({
                'tipo': 'hipertension',
                'mensaje': f'Presión sistólica elevada: {self.presion_sistolica} mmHg',
                'clase': 'warning',
                'icono': 'heart-pulse'
            })
        
        if self.presion_diastolica and self.presion_diastolica >= 90:
            alertas.append({
                'tipo': 'hipertension',
                'mensaje': f'Presión diastólica elevada: {self.presion_diastolica} mmHg',
                'clase': 'warning',
                'icono': 'heart-pulse'
            })
        
        if self.imc and self.imc > 30:
            alertas.append({
                'tipo': 'obesidad',
                'mensaje': f'IMC elevado: {self.imc} (Obesidad)',
                'clase': 'info',
                'icono': 'person'
            })
        
        return alertas
    
    @property
    def presion_arterial(self):
        """Retorna presión arterial en formato 120/80"""
        if self.presion_sistolica and self.presion_diastolica:
            return f"{self.presion_sistolica}/{self.presion_diastolica}"
        return None
    
    @property
    def clasificacion_imc(self):
        """Retorna clasificación del IMC"""
        if not self.imc:
            return None
        if self.imc < 18.5:
            return 'Bajo peso'
        elif self.imc < 25:
            return 'Normal'
        elif self.imc < 30:
            return 'Sobrepeso'
        else:
            return 'Obesidad'

