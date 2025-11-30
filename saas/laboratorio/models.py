from datetime import datetime
from saas.extensions import db

class OrdenLaboratorio(db.Model):
    """Órdenes de laboratorio. TODO: Catálogo de exámenes"""
    __tablename__ = 'ordenes_laboratorio'
    
    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, nullable=False, default=1)
    codigo_orden = db.Column(db.String(20), unique=True, index=True)
    
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False, index=True)
    medico_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, index=True)
    
    fecha_orden = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    examenes_solicitados = db.Column(db.Text, nullable=False)  # TODO: Relación con tabla exámenes
    indicaciones = db.Column(db.Text)
    urgente = db.Column(db.Boolean, default=False, index=True)
    
    estado = db.Column(db.String(30), default='pendiente', index=True)  # pendiente, en_proceso, completada
    fecha_resultado = db.Column(db.DateTime)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    paciente = db.relationship('Paciente', backref='ordenes_laboratorio')
    medico = db.relationship('Usuario', backref='ordenes_laboratorio', foreign_keys=[medico_id])
    
    def generar_codigo(self):
        año = datetime.utcnow().year
        ultimo_id = db.session.query(db.func.max(OrdenLaboratorio.id)).scalar() or 0
        self.codigo_orden = f'LAB-{año}-{str(ultimo_id + 1).zfill(4)}'

class ResultadoLaboratorio(db.Model):
    """Resultados de exámenes. TODO: Valores de referencia"""
    __tablename__ = 'resultados_laboratorio'
    
    id = db.Column(db.Integer, primary_key=True)
    orden_id = db.Column(db.Integer, db.ForeignKey('ordenes_laboratorio.id'), nullable=False, index=True)
    
    examen = db.Column(db.String(100), nullable=False)
    resultado = db.Column(db.Text, nullable=False)
    valor_referencia = db.Column(db.String(100))
    observaciones = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    orden = db.relationship('OrdenLaboratorio', backref='resultados')
