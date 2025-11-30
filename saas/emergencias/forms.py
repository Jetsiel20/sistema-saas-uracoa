from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, FloatField, SelectField, DateTimeField
from wtforms.validators import DataRequired, Optional, NumberRange

class EmergenciaForm(FlaskForm):
    """
    Formulario simplificado para triage de emergencias
    Solo 7 campos esenciales: búsqueda paciente + nivel triage + tipo + llegada + motivo + 3 signos vitales
    """
    # Triage - PRIORIDAD 1
    nivel_triage = SelectField(
        'Nivel de Triage',
        choices=[
            (1, '1 - Resucitación (Rojo) - Inmediato'),
            (2, '2 - Emergencia (Naranja) - 10 min'),
            (3, '3 - Urgencia (Amarillo) - 30 min'),
            (4, '4 - Menos Urgente (Verde) - 60 min'),
            (5, '5 - No Urgente (Azul) - 120 min')
        ],
        coerce=int,
        validators=[DataRequired(message='Debe seleccionar el nivel de triage')]
    )
    
    # Datos de ingreso
    tipo_emergencia = SelectField(
        'Tipo de Emergencia',
        choices=[
            ('trauma', 'Trauma/Accidente'),
            ('cardiaca', 'Emergencia Cardíaca'),
            ('respiratoria', 'Dificultad Respiratoria'),
            ('neurologica', 'Emergencia Neurológica'),
            ('obstetrica', 'Emergencia Obstétrica'),
            ('pediatrica', 'Emergencia Pediátrica'),
            ('toxicologica', 'Intoxicación/Envenenamiento'),
            ('quemadura', 'Quemaduras'),
            ('otra', 'Otra')
        ],
        validators=[DataRequired(message='Seleccione el tipo de emergencia')]
    )
    
    medio_llegada = SelectField(
        'Medio de Llegada',
        choices=[
            ('ambulancia', 'Ambulancia'),
            ('caminando', 'Caminando'),
            ('vehiculo_particular', 'Vehículo Particular'),
            ('policia', 'Policía'),
            ('bomberos', 'Bomberos'),
            ('otro', 'Otro')
        ],
        validators=[DataRequired(message='Indique cómo llegó el paciente')]
    )
    
    # Motivo
    motivo_consulta = TextAreaField(
        'Motivo de la Emergencia',
        validators=[DataRequired(message='Describa el motivo de la emergencia')],
        render_kw={'rows': 3, 'placeholder': 'Describa brevemente qué le pasó al paciente...'}
    )
    
    # Signos vitales básicos (solo 4 esenciales)
    temperatura = FloatField(
        'Temperatura',
        validators=[Optional(), NumberRange(min=30.0, max=45.0, message='Temperatura debe estar entre 30-45°C')],
        render_kw={'placeholder': '36.5', 'step': '0.1'}
    )
    presion_sistolica = IntegerField(
        'Presión Sistólica',
        validators=[Optional(), NumberRange(min=50, max=250, message='Presión sistólica: 50-250 mmHg')],
        render_kw={'placeholder': '120'}
    )
    presion_diastolica = IntegerField(
        'Presión Diastólica',
        validators=[Optional(), NumberRange(min=30, max=150, message='Presión diastólica: 30-150 mmHg')],
        render_kw={'placeholder': '80'}
    )
    frecuencia_cardiaca = IntegerField(
        'Frecuencia Cardíaca',
        validators=[Optional(), NumberRange(min=30, max=220, message='Frecuencia cardíaca: 30-220 BPM')],
        render_kw={'placeholder': '75'}
    )
