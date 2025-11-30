from datetime import datetime
from saas.extensions import db

class Cama(db.Model):
    """
    Modelo para gestión de camas hospitalarias.
    Estados: libre, ocupada, mantenimiento
    """
    __tablename__ = 'camas'
    
    id = db.Column(db.Integer, primary_key=True)
    codigo = db.Column(db.String(20), unique=True, nullable=False, index=True)  # ej: A-101, B-205
    sala = db.Column(db.String(50), nullable=False, index=True)  # ej: Sala A, UCI, Pediatría
    estado = db.Column(db.String(20), nullable=False, default='libre', index=True)
    # Estados: libre, ocupada, mantenimiento
    
    # Relaciones
    internados = db.relationship('Internado', backref='cama', lazy='dynamic')
    
    @property
    def ocupante_actual(self):
        """Retorna el internado activo en esta cama"""
        return self.internados.filter_by(estado='activo').first()
    
    @property
    def color_estado(self):
        """Color badge según estado"""
        colores = {
            'libre': 'success',
            'ocupada': 'danger',
            'mantenimiento': 'warning'
        }
        return colores.get(self.estado, 'secondary')
    
    def __repr__(self):
        return f'<Cama {self.codigo} - {self.estado}>'


class Internado(db.Model):
    """
    Modelo para registro de pacientes internados.
    """
    __tablename__ = 'internados_registro'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Relaciones
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False, index=True)
    cama_id = db.Column(db.Integer, db.ForeignKey('camas.id'), nullable=False, index=True)
    medico_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False, index=True)
    
    # Datos de internación
    fecha_ingreso = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    fecha_alta = db.Column(db.DateTime, index=True)
    
    motivo = db.Column(db.Text, nullable=False)
    diagnostico_inicial = db.Column(db.Text, nullable=False)
    
    # Estado
    estado = db.Column(db.String(20), nullable=False, default='activo', index=True)
    # Estados: activo, alta
    
    # Información adicional
    tipo_alta = db.Column(db.String(50))  # medica, voluntaria, referencia, fallecimiento
    observaciones_alta = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    # Relaciones
    paciente = db.relationship('Paciente', backref='internaciones')
    medico = db.relationship('Usuario', backref='pacientes_internados', foreign_keys=[medico_id])
    evoluciones = db.relationship('Evolucion', backref='internado', lazy='dynamic', 
                                  cascade='all, delete-orphan', order_by='Evolucion.fecha.desc()')
    
    @property
    def dias_internado(self):
        """Calcula días de internación"""
        fin = self.fecha_alta or datetime.utcnow()
        delta = fin - self.fecha_ingreso
        return delta.days
    
    @property
    def estado_traducido(self):
        """Estado en español"""
        return 'Activo' if self.estado == 'activo' else 'Alta'
    
    def __repr__(self):
        return f'<Internado {self.id} - Paciente: {self.paciente_id} - {self.estado}>'


class Evolucion(db.Model):
    """
    Modelo para evoluciones diarias de pacientes internados.
    """
    __tablename__ = 'evoluciones'
    
    id = db.Column(db.Integer, primary_key=True)
    internado_id = db.Column(db.Integer, db.ForeignKey('internados_registro.id'), nullable=False, index=True)
    
    fecha = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    notas = db.Column(db.Text, nullable=False)
    
    # Signos vitales
    temperatura = db.Column(db.Float)
    presion_sistolica = db.Column(db.Integer)
    presion_diastolica = db.Column(db.Integer)
    frecuencia_cardiaca = db.Column(db.Integer)
    frecuencia_respiratoria = db.Column(db.Integer)
    saturacion = db.Column(db.Integer)
    
    # Quien registró la evolución
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    usuario = db.relationship('Usuario', backref='evoluciones_registradas')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Evolucion {self.id} - Internado: {self.internado_id}>'
