from flask_wtf import FlaskForm
from wtforms import SelectField, TextAreaField
from wtforms.validators import DataRequired

class AsignacionEnfermeroForm(FlaskForm):
    """Formulario para asignar enfermero a paciente internado"""
    enfermero_id = SelectField('Enfermero', coerce=int, validators=[DataRequired()])
    paciente_id = SelectField('Paciente', coerce=int, validators=[DataRequired()])
    observaciones = TextAreaField('Observaciones')
