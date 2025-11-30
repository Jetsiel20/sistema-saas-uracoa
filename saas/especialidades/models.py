from datetime import datetime
from saas.extensions import db

class Especialidad(db.Model):
    """Registro de médicos especialistas y sus turnos"""
    __tablename__ = 'especialidades'
    
    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, nullable=False, default=1)
    nombre_medico = db.Column(db.String(100), nullable=False, index=True)
    especialidad = db.Column(db.String(80), nullable=False)
    telefono_contacto = db.Column(db.String(20), nullable=False)
    turno = db.Column(db.String(20), nullable=False)  # Mañana, Tarde, Noche
    activo = db.Column(db.Boolean, default=True, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Especialidad {self.nombre_medico} - {self.especialidad}>'
