from datetime import datetime
from saas.extensions import db

class Emergencia(db.Model):
    """
    Modelo para emergencias médicas con sistema de triage.
    Niveles: 1=Rojo (Crítico), 2=Naranja (Urgente), 3=Amarillo (Moderado), 
             4=Verde (Menor), 5=Azul (No urgente)
    """
    __tablename__ = 'emergencias'
    
    # Identificadores
    id = db.Column(db.Integer, primary_key=True)
    
    # Relaciones (paciente_id es opcional para casos sin identificar)
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=True, index=True)
    atendido_por = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True, index=True)
    
    # Información de ingreso
    hora_ingreso = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Tipo de emergencia
    tipo = db.Column(db.String(50), nullable=False, index=True)
    # Opciones: accidente, respiratoria, cardiaca, otra
    
    # Sistema de triage
    triage_nivel = db.Column(db.Integer, nullable=False, index=True)
    # 1 = Rojo (resucitación), 2 = Naranja (emergencia), 3 = Amarillo (urgente),
    # 4 = Verde (menos urgente), 5 = Azul (no urgente)
    
    descripcion = db.Column(db.Text, nullable=False)
    
    # Estado del paciente
    estado = db.Column(db.String(20), nullable=False, default='en_triaje', index=True)
    # Estados: en_triaje, en_atencion, derivado, alta
    
    # Signos vitales al ingreso
    presion_arterial = db.Column(db.String(20))  # ej: 120/80
    frecuencia_cardiaca = db.Column(db.Integer)  # BPM
    temperatura = db.Column(db.Float)  # °C
    saturacion = db.Column(db.Integer)  # SpO2 %
    glasgow = db.Column(db.Integer)  # Escala de Glasgow (3-15)
    
    # Observaciones y seguimiento
    observaciones = db.Column(db.Text)
    diagnostico_preliminar = db.Column(db.Text)
    tratamiento = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    hora_atencion = db.Column(db.DateTime)  # Cuando comienza la atención
    hora_alta = db.Column(db.DateTime)  # Cuando se da de alta
    
    # Relaciones
    paciente = db.relationship('Paciente', backref='emergencias', foreign_keys=[paciente_id])
    medico = db.relationship('Usuario', backref='emergencias_atendidas', foreign_keys=[atendido_por])
    
    @property
    def color_triage(self):
        """Retorna el color según nivel de triage"""
        colores = {
            1: 'danger',    # Rojo
            2: 'warning',   # Naranja
            3: 'yellow',    # Amarillo
            4: 'success',   # Verde
            5: 'info'       # Azul
        }
        return colores.get(self.triage_nivel, 'secondary')
    
    @property
    def nombre_triage(self):
        """Retorna el nombre del nivel de triage"""
        nombres = {
            1: 'Crítico (Rojo)',
            2: 'Urgente (Naranja)',
            3: 'Moderado (Amarillo)',
            4: 'Menor (Verde)',
            5: 'No Urgente (Azul)'
        }
        return nombres.get(self.triage_nivel, 'Desconocido')
    
    @property
    def tiempo_espera(self):
        """Calcula el tiempo de espera en minutos"""
        if self.hora_atencion:
            delta = self.hora_atencion - self.hora_ingreso
            return int(delta.total_seconds() / 60)
        else:
            delta = datetime.utcnow() - self.hora_ingreso
            return int(delta.total_seconds() / 60)
    
    @property
    def estado_traducido(self):
        """Retorna estado en español legible"""
        estados = {
            'en_triaje': 'En Triaje',
            'en_atencion': 'En Atención',
            'derivado': 'Derivado',
            'alta': 'Alta'
        }
        return estados.get(self.estado, self.estado)
    
    def __repr__(self):
        return f'<Emergencia {self.id} - Nivel {self.triage_nivel} - {self.estado}>'
