"""
Formularios del Módulo Principal
Hospital Tipo 1 Uracoa - J&S Software Inteligentes
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, DateField, SelectField, IntegerField, FloatField, BooleanField, SubmitField, DateTimeField
from wtforms.validators import DataRequired, Email, Length, Optional, NumberRange, ValidationError
from datetime import datetime
from saas.models import Paciente


class PacienteForm(FlaskForm):
    """Formulario para crear/editar paciente"""
    # Información personal
    cedula = StringField('Cédula', validators=[
        DataRequired(message='La cédula es requerida'),
        Length(min=6, max=20)
    ])
    nombre = StringField('Nombre', validators=[
        DataRequired(message='El nombre es requerido'),
        Length(min=2, max=100)
    ])
    apellido = StringField('Apellido', validators=[
        DataRequired(message='El apellido es requerido'),
        Length(min=2, max=100)
    ])
    fecha_nacimiento = DateField('Fecha de Nacimiento', validators=[
        DataRequired(message='La fecha de nacimiento es requerida')
    ])
    sexo = SelectField('Sexo', choices=[
        ('', 'Seleccione...'),
        ('Masculino', 'Masculino'),
        ('Femenino', 'Femenino')
    ], validators=[DataRequired()])
    
    # Contacto
    telefono = StringField('Teléfono', validators=[Length(max=20)])
    email = StringField('Email', validators=[Email(message='Email inválido'), Optional()])
    direccion = TextAreaField('Dirección', validators=[Length(max=500)])
    ciudad = StringField('Ciudad', validators=[Length(max=100)])
    estado = StringField('Estado', validators=[Length(max=100)])
    
    # Información médica
    tipo_sangre = SelectField('Tipo de Sangre', choices=[
        ('', 'Desconocido'),
        ('A+', 'A+'), ('A-', 'A-'),
        ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'),
        ('O+', 'O+'), ('O-', 'O-')
    ])
    alergias = TextAreaField('Alergias', validators=[Length(max=1000)])
    condiciones_cronicas = TextAreaField('Condiciones Crónicas', validators=[Length(max=1000)])
    
    # Contacto de emergencia
    contacto_emergencia_nombre = StringField('Nombre Contacto de Emergencia', validators=[Length(max=200)])
    contacto_emergencia_telefono = StringField('Teléfono de Emergencia', validators=[Length(max=20)])
    contacto_emergencia_relacion = StringField('Relación', validators=[Length(max=50)])
    
    # Médico tratante
    medico_id = SelectField('Médico Tratante', coerce=int, validators=[Optional()])
    
    submit = SubmitField('Guardar Paciente')
    
    def __init__(self, paciente_id=None, *args, **kwargs):
        super(PacienteForm, self).__init__(*args, **kwargs)
        self.paciente_id = paciente_id
    
    def validate_cedula(self, cedula):
        """Validar que la cédula no exista"""
        paciente = Paciente.query.filter_by(cedula=cedula.data).first()
        if paciente and (self.paciente_id is None or paciente.id != self.paciente_id):
            raise ValidationError('Esta cédula ya está registrada.')


class CitaForm(FlaskForm):
    """Formulario para crear/editar cita"""
    paciente_id = SelectField('Paciente', coerce=int, validators=[
        DataRequired(message='Debe seleccionar un paciente')
    ])
    medico_id = SelectField('Médico', coerce=int, validators=[
        DataRequired(message='Debe seleccionar un médico')
    ])
    fecha_hora = DateTimeField('Fecha y Hora', format='%Y-%m-%dT%H:%M', validators=[
        DataRequired(message='La fecha y hora son requeridas')
    ])
    duracion_minutos = IntegerField('Duración (minutos)', default=30, validators=[
        NumberRange(min=15, max=480, message='La duración debe estar entre 15 y 480 minutos')
    ])
    motivo = TextAreaField('Motivo de la Cita', validators=[
        DataRequired(message='El motivo es requerido'),
        Length(max=1000)
    ])
    tipo_cita = SelectField('Tipo de Cita', choices=[
        ('consulta', 'Consulta General'),
        ('control', 'Control'),
        ('emergencia', 'Emergencia'),
        ('cirugia', 'Cirugía'),
        ('procedimiento', 'Procedimiento')
    ], validators=[DataRequired()])
    estado = SelectField('Estado', choices=[
        ('programada', 'Programada'),
        ('confirmada', 'Confirmada'),
        ('en_curso', 'En Curso'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
        ('no_asistio', 'No Asistió')
    ], default='programada')
    observaciones = TextAreaField('Observaciones', validators=[Length(max=1000)])
    
    submit = SubmitField('Guardar Cita')
    
    def validate_fecha_hora(self, fecha_hora):
        """Validar que la fecha no sea en el pasado"""
        if fecha_hora.data < datetime.now():
            raise ValidationError('No se pueden programar citas en el pasado.')


class HistoriaClinicaForm(FlaskForm):
    """Formulario para crear historia clínica"""
    paciente_id = SelectField('Paciente', coerce=int, validators=[
        DataRequired(message='Debe seleccionar un paciente')
    ])
    cita_id = SelectField('Cita (opcional)', coerce=int, validators=[Optional()])
    
    # Motivo de consulta
    motivo_consulta = TextAreaField('Motivo de Consulta', validators=[
        DataRequired(message='El motivo de consulta es requerido'),
        Length(max=1000)
    ])
    
    # Signos vitales
    peso = FloatField('Peso (kg)', validators=[
        Optional(),
        NumberRange(min=0, max=500, message='Peso inválido')
    ])
    altura = FloatField('Altura (cm)', validators=[
        Optional(),
        NumberRange(min=0, max=300, message='Altura inválida')
    ])
    temperatura = FloatField('Temperatura (°C)', validators=[
        Optional(),
        NumberRange(min=30, max=45, message='Temperatura inválida')
    ])
    presion_arterial = StringField('Presión Arterial', validators=[Length(max=20)])
    frecuencia_cardiaca = IntegerField('Frecuencia Cardíaca (ppm)', validators=[
        Optional(),
        NumberRange(min=30, max=250, message='Frecuencia cardíaca inválida')
    ])
    frecuencia_respiratoria = IntegerField('Frecuencia Respiratoria (rpm)', validators=[
        Optional(),
        NumberRange(min=5, max=60, message='Frecuencia respiratoria inválida')
    ])
    
    # Evaluación médica
    sintomas = TextAreaField('Síntomas', validators=[Length(max=2000)])
    examen_fisico = TextAreaField('Examen Físico', validators=[Length(max=2000)])
    diagnostico = TextAreaField('Diagnóstico', validators=[
        DataRequired(message='El diagnóstico es requerido'),
        Length(max=2000)
    ])
    plan_tratamiento = TextAreaField('Plan de Tratamiento', validators=[Length(max=2000)])
    
    # Prescripciones
    medicamentos = TextAreaField('Medicamentos Recetados', validators=[Length(max=2000)])
    examenes_solicitados = TextAreaField('Exámenes Solicitados', validators=[Length(max=2000)])
    
    # Seguimiento
    proxima_cita = DateField('Próxima Cita', validators=[Optional()])
    observaciones = TextAreaField('Observaciones', validators=[Length(max=2000)])
    
    submit = SubmitField('Guardar Historia Clínica')
