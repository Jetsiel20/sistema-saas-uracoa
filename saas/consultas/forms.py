from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FloatField, IntegerField, SelectField, DateTimeField, HiddenField
from wtforms.validators import DataRequired, Optional, NumberRange, Length, ValidationError

class ConsultaForm(FlaskForm):
    """
    Formulario robusto para consultas médicas con validaciones de rangos médicos.
    """
    # ID de paciente (oculto, viene de búsqueda AJAX)
    paciente_id = HiddenField(
        'Paciente',
        validators=[DataRequired(message='Debe buscar y seleccionar un paciente')]
    )
    
    # Motivo de consulta
    motivo = TextAreaField(
        'Motivo de Consulta',
        validators=[DataRequired(message='El motivo es obligatorio'), Length(min=10, max=200)],
        render_kw={
            'rows': 3,
            'placeholder': 'Describa brevemente el motivo de la consulta (máx. 200 caracteres)...',
            'class': 'form-control',
            'maxlength': '200'
        }
    )
    
    # Signos vitales con validaciones de rangos médicos
    temperatura = FloatField(
        'Temperatura (°C)',
        validators=[
            Optional(),
            NumberRange(min=35.0, max=42.0, message='Temperatura debe estar entre 35°C y 42°C')
        ],
        render_kw={
            'placeholder': '36.5',
            'class': 'form-control',
            'step': '0.1',
            'title': 'Temperatura corporal en grados Celsius'
        }
    )
    
    presion_sistolica = IntegerField(
        'Presión Sistólica (mmHg)',
        validators=[
            Optional(),
            NumberRange(min=70, max=250, message='Presión sistólica debe estar entre 70 y 250 mmHg')
        ],
        render_kw={
            'placeholder': '120',
            'class': 'form-control',
            'title': 'Presión arterial sistólica (valor superior)'
        }
    )
    
    presion_diastolica = IntegerField(
        'Presión Diastólica (mmHg)',
        validators=[
            Optional(),
            NumberRange(min=40, max=150, message='Presión diastólica debe estar entre 40 y 150 mmHg')
        ],
        render_kw={
            'placeholder': '80',
            'class': 'form-control',
            'title': 'Presión arterial diastólica (valor inferior)'
        }
    )
    
    frecuencia_cardiaca = IntegerField(
        'Frecuencia Cardíaca (BPM)',
        validators=[
            Optional(),
            NumberRange(min=30, max=220, message='Frecuencia cardíaca debe estar entre 30 y 220 BPM')
        ],
        render_kw={
            'placeholder': '75',
            'class': 'form-control',
            'title': 'Latidos por minuto'
        }
    )
    
    peso = FloatField(
        'Peso (kg)',
        validators=[
            Optional(),
            NumberRange(min=2.0, max=300.0, message='Peso debe estar entre 2 y 300 kg')
        ],
        render_kw={
            'placeholder': '70.5',
            'class': 'form-control',
            'step': '0.1',
            'title': 'Peso corporal en kilogramos'
        }
    )
    
    altura = FloatField(
        'Altura (cm)',
        validators=[
            Optional(),
            NumberRange(min=40.0, max=250.0, message='Altura debe estar entre 40 y 250 cm')
        ],
        render_kw={
            'placeholder': '170',
            'class': 'form-control',
            'step': '0.1',
            'title': 'Altura en centímetros'
        }
    )
    
    # TODO MEJORAS: Diagnóstico y tratamiento se completarán en módulo médico
    
    # Datos contextuales rurales
    sector = StringField(
        'Sector / Comunidad Rural',
        validators=[Optional(), Length(max=120)],
        render_kw={
            'placeholder': 'Ej: La Veguita, El Carmen, etc.',
            'class': 'form-control',
            'title': 'Sector o comunidad de procedencia del paciente'
        }
    )
    
    nivel_conciencia = SelectField(
        'Nivel de Conciencia',
        choices=[
            ('', 'Seleccione...'),
            ('Alerta', 'Alerta'),
            ('Somnoliento', 'Somnoliento'),
            ('Inconsciente', 'Inconsciente')
        ],
        validators=[Optional()],
        render_kw={
            'class': 'form-select',
            'title': 'Estado de conciencia del paciente'
        }
    )
    
    def validate_presion_diastolica(self, field):
        """Validación cruzada: presión diastólica debe ser menor que sistólica"""
        if field.data and self.presion_sistolica.data:
            if field.data >= self.presion_sistolica.data:
                raise ValidationError('La presión diastólica debe ser menor que la sistólica')
    
    def validate_peso(self, field):
        """Validación adicional para peso con altura (IMC razonable)"""
        if field.data and self.altura.data:
            altura_metros = self.altura.data / 100
            imc = field.data / (altura_metros ** 2)
            if imc < 10 or imc > 80:
                raise ValidationError('La combinación de peso y altura resulta en un IMC fuera de rango razonable')
