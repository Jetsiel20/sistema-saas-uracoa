from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField, DateTimeField, IntegerField, FloatField
from wtforms.validators import DataRequired, Optional, NumberRange, Length

class InternadoForm(FlaskForm):
    """Formulario para registrar nueva internación"""
    paciente_id = SelectField('Paciente', coerce=int, validators=[DataRequired()])
    cama_id = SelectField('Cama', coerce=int, validators=[DataRequired()])
    medico_id = SelectField('Médico Responsable', coerce=int, validators=[DataRequired()])
    
    fecha_ingreso = DateTimeField('Fecha y Hora de Ingreso', 
                                   format='%Y-%m-%dT%H:%M',
                                   validators=[DataRequired()])
    
    motivo = TextAreaField('Motivo de Internación', 
                           validators=[DataRequired(), Length(min=10, max=1000)],
                           render_kw={'rows': 3, 'placeholder': 'Describa el motivo de la internación...'})
    
    diagnostico_inicial = TextAreaField('Diagnóstico Inicial', 
                                        validators=[DataRequired(), Length(min=10, max=1000)],
                                        render_kw={'rows': 3, 'placeholder': 'Diagnóstico preliminar...'})


class AltaForm(FlaskForm):
    """Formulario para dar alta a paciente internado"""
    tipo_alta = SelectField('Tipo de Alta',
                           choices=[
                               ('medica', 'Alta Médica'),
                               ('voluntaria', 'Alta Voluntaria'),
                               ('referencia', 'Referencia/Transferencia'),
                               ('fallecimiento', 'Fallecimiento')
                           ],
                           validators=[DataRequired()])
    
    observaciones_alta = TextAreaField('Observaciones de Alta',
                                      validators=[DataRequired(), Length(min=10, max=1000)],
                                      render_kw={'rows': 4, 'placeholder': 'Indicaciones, tratamiento ambulatorio, controles...'})


class EvolucionForm(FlaskForm):
    """Formulario para registrar evolución diaria"""
    notas = TextAreaField('Notas de Evolución',
                         validators=[DataRequired(), Length(min=10, max=2000)],
                         render_kw={'rows': 4, 'placeholder': 'Estado general, síntomas, respuesta al tratamiento...'})
    
    # Signos vitales
    temperatura = FloatField('Temperatura (°C)',
                            validators=[Optional(), NumberRange(min=35, max=42)],
                            render_kw={'placeholder': '36.5', 'step': '0.1'})
    
    presion_sistolica = IntegerField('Presión Sistólica (mmHg)',
                                     validators=[Optional(), NumberRange(min=70, max=200)],
                                     render_kw={'placeholder': '120'})
    
    presion_diastolica = IntegerField('Presión Diastólica (mmHg)',
                                      validators=[Optional(), NumberRange(min=40, max=140)],
                                      render_kw={'placeholder': '80'})
    
    frecuencia_cardiaca = IntegerField('Frecuencia Cardíaca (BPM)',
                                       validators=[Optional(), NumberRange(min=40, max=200)],
                                       render_kw={'placeholder': '75'})
    
    frecuencia_respiratoria = IntegerField('Frecuencia Respiratoria (RPM)',
                                           validators=[Optional(), NumberRange(min=8, max=40)],
                                           render_kw={'placeholder': '16'})
    
    saturacion = IntegerField('Saturación O₂ (%)',
                             validators=[Optional(), NumberRange(min=70, max=100)],
                             render_kw={'placeholder': '98'})


class CamaForm(FlaskForm):
    """Formulario para gestionar camas"""
    codigo = StringField('Código de Cama',
                        validators=[DataRequired(), Length(min=2, max=20)],
                        render_kw={'placeholder': 'A-101, UCI-5, PED-12'})
    
    sala = StringField('Sala/Área',
                      validators=[DataRequired(), Length(max=50)],
                      render_kw={'placeholder': 'Sala A, UCI, Pediatría'})
    
    estado = SelectField('Estado',
                        choices=[
                            ('libre', 'Libre'),
                            ('ocupada', 'Ocupada'),
                            ('mantenimiento', 'En Mantenimiento')
                        ],
                        validators=[DataRequired()])
