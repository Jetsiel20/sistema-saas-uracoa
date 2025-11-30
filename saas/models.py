"""
Modelos de Base de Datos - Hospital Tipo 1 Uracoa
J&S Software Inteligentes
"""
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from saas.extensions import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    """Cargar usuario para Flask-Login"""
    return Usuario.query.get(int(user_id))


class Usuario(UserMixin, db.Model):
    """Modelo de Usuario del sistema"""
    __tablename__ = 'usuarios'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Información personal
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    cedula = db.Column(db.String(20), unique=True, index=True)
    telefono = db.Column(db.String(20))
    
    # Rol y permisos
    rol = db.Column(db.String(50), nullable=False, default='usuario')
    # Roles: admin, medico, enfermera, recepcionista, farmacia, laboratorio
    
    especialidad = db.Column(db.String(100))  # Para médicos
    codigo_profesional = db.Column(db.String(50))  # Colegiatura/Registro profesional
    
    # Estado y fechas
    activo = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    ultimo_acceso = db.Column(db.DateTime)
    
    # Relaciones (optimized with lazy='select' to avoid N+1 queries)
    pacientes_atendidos = db.relationship('Paciente', backref='medico_tratante', lazy='select',
                                          foreign_keys='Paciente.medico_id')
    citas_asignadas = db.relationship('Cita', backref='medico', lazy='select')
    historias_creadas = db.relationship('HistoriaClinica', backref='medico', lazy='select')
    
    def set_password(self, password):
        """Generar hash de contraseña"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Verificar contraseña"""
        return check_password_hash(self.password_hash, password)
    
    @property
    def nombre_completo(self):
        """Retornar nombre completo"""
        return f"{self.nombre} {self.apellido}"
    
    @property
    def es_admin(self):
        return self.rol == 'admin'
    
    @property
    def es_medico(self):
        return self.rol == 'medico'
    
    def __repr__(self):
        return f'<Usuario {self.username} - {self.rol}>'


class Paciente(db.Model):
    """Modelo de Paciente"""
    __tablename__ = 'pacientes'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Información personal
    cedula = db.Column(db.String(20), unique=True, nullable=False, index=True)
    nombre = db.Column(db.String(100), nullable=False)
    apellido = db.Column(db.String(100), nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=False)
    sexo = db.Column(db.String(10), nullable=False)  # Masculino, Femenino
    
    # Contacto
    telefono = db.Column(db.String(20))
    email = db.Column(db.String(120))
    direccion = db.Column(db.Text)
    ciudad = db.Column(db.String(100))
    estado = db.Column(db.String(100))
    
    # Información médica básica
    tipo_sangre = db.Column(db.String(10))
    alergias = db.Column(db.Text)
    condiciones_cronicas = db.Column(db.Text)
    
    # Seguro médico
    tiene_seguro = db.Column(db.Boolean, default=False)
    aseguradora = db.Column(db.String(100))
    numero_poliza = db.Column(db.String(100))
    
    # Contacto de emergencia
    contacto_emergencia_nombre = db.Column(db.String(200))
    contacto_emergencia_telefono = db.Column(db.String(20))
    contacto_emergencia_relacion = db.Column(db.String(50))
    
    # Asignación
    medico_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    
    # Estado y fechas
    activo = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    ultima_consulta = db.Column(db.DateTime)
    
    # Relaciones (optimized with lazy='select' to avoid N+1 queries)
    citas = db.relationship('Cita', backref='paciente', lazy='select', cascade='all, delete-orphan')
    historias_clinicas = db.relationship('HistoriaClinica', backref='paciente', 
                                        lazy='select', cascade='all, delete-orphan')
    
    @property
    def nombre_completo(self):
        return f"{self.nombre} {self.apellido}"
    
    @property
    def edad(self):
        """Calcular edad del paciente"""
        if self.fecha_nacimiento:
            today = datetime.now().date()
            return today.year - self.fecha_nacimiento.year - \
                   ((today.month, today.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day))
        return None
    
    def __repr__(self):
        return f'<Paciente {self.nombre_completo} - {self.cedula}>'


class Cita(db.Model):
    """Modelo de Citas Médicas"""
    __tablename__ = 'citas'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Relaciones
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False)
    medico_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    
    # Información de la cita
    fecha_hora = db.Column(db.DateTime, nullable=False, index=True)
    duracion_minutos = db.Column(db.Integer, default=30)
    motivo = db.Column(db.Text, nullable=False)
    tipo_cita = db.Column(db.String(50), default='consulta')
    # Tipos: consulta, control, emergencia, cirugia, procedimiento
    
    # Estado
    estado = db.Column(db.String(50), default='programada')
    # Estados: programada, confirmada, en_curso, completada, cancelada, no_asistio
    
    # Observaciones
    observaciones = db.Column(db.Text)
    diagnostico_preliminar = db.Column(db.Text)
    
    # Fechas
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Cita {self.id} - {self.fecha_hora} - {self.estado}>'


class HistoriaClinica(db.Model):
    """Modelo de Historia Clínica / Consulta"""
    __tablename__ = 'historias_clinicas'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Relaciones
    paciente_id = db.Column(db.Integer, db.ForeignKey('pacientes.id'), nullable=False)
    medico_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=False)
    cita_id = db.Column(db.Integer, db.ForeignKey('citas.id'))
    
    # Información de la consulta
    fecha_consulta = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    motivo_consulta = db.Column(db.Text, nullable=False)
    
    # Examen físico
    peso = db.Column(db.Float)  # kg
    altura = db.Column(db.Float)  # cm
    temperatura = db.Column(db.Float)  # °C
    presion_arterial = db.Column(db.String(20))  # ej: 120/80
    frecuencia_cardiaca = db.Column(db.Integer)  # ppm
    frecuencia_respiratoria = db.Column(db.Integer)  # rpm
    
    # Evaluación médica
    sintomas = db.Column(db.Text)
    examen_fisico = db.Column(db.Text)
    diagnostico = db.Column(db.Text, nullable=False)
    plan_tratamiento = db.Column(db.Text)
    
    # Prescripciones
    medicamentos = db.Column(db.Text)  # JSON o texto estructurado
    examenes_solicitados = db.Column(db.Text)
    
    # Seguimiento
    proxima_cita = db.Column(db.Date)
    observaciones = db.Column(db.Text)
    
    # Fechas
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    fecha_actualizacion = db.Column(db.DateTime, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<HistoriaClinica {self.id} - Paciente: {self.paciente_id}>'


class Medicamento(db.Model):
    """Modelo de Medicamentos (Inventario Institucional)"""
    __tablename__ = 'medicamentos'
    
    id = db.Column(db.Integer, primary_key=True)
    
    # Información del medicamento
    nombre = db.Column(db.String(200), nullable=False)
    nombre_generico = db.Column(db.String(200))
    presentacion = db.Column(db.String(100))  # tabletas, jarabe, inyectable, etc.
    concentracion = db.Column(db.String(100))  # ej: 500mg, 10mg/ml
    
    # Código y registro
    codigo_barras = db.Column(db.String(100), unique=True)
    registro_sanitario = db.Column(db.String(100))
    laboratorio = db.Column(db.String(200))
    
    # Inventario
    cantidad_stock = db.Column(db.Integer, default=0)
    unidad_medida = db.Column(db.String(50))
    stock_minimo = db.Column(db.Integer, default=10)
    
    # Control institucional (sin precios)
    responsable_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'))
    observaciones = db.Column(db.Text)
    
    # Fechas
    fecha_vencimiento = db.Column(db.Date)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Estado
    activo = db.Column(db.Boolean, default=True)
    requiere_receta = db.Column(db.Boolean, default=True)
    
    # Relación con responsable
    responsable = db.relationship('Usuario', foreign_keys=[responsable_id], backref='medicamentos_asignados')
    
    @property
    def stock_bajo(self):
        """Retorna True si el stock está por debajo del mínimo"""
        return self.cantidad_stock <= self.stock_minimo
    
    @property
    def estado_vencimiento(self):
        """Retorna estado según fecha de vencimiento"""
        if not self.fecha_vencimiento:
            return None
        
        from datetime import date, timedelta
        hoy = date.today()
        dias_para_vencer = (self.fecha_vencimiento - hoy).days
        
        if dias_para_vencer < 0:
            return 'vencido'
        elif dias_para_vencer <= 30:
            return 'por_vencer'
        else:
            return 'vigente'
    
    def __repr__(self):
        return f'<Medicamento {self.nombre} - Stock: {self.cantidad_stock}>'
