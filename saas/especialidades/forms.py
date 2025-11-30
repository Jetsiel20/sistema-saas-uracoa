from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length

class EspecialidadForm(FlaskForm):
    nombre_medico = StringField('Nombre del Médico', validators=[DataRequired(), Length(max=100)])
    especialidad = SelectField('Especialidad', choices=[
        ('Medicina General', 'Medicina General'),
        ('Pediatría', 'Pediatría'),
        ('Ginecología', 'Ginecología'),
        ('Odontología', 'Odontología'),
        ('Cardiología', 'Cardiología'),
        ('Traumatología', 'Traumatología'),
        ('Otra', 'Otra')
    ], validators=[DataRequired()])
    telefono_contacto = StringField('Teléfono', validators=[DataRequired(), Length(max=20)])
    turno = SelectField('Turno', choices=[
        ('Mañana', 'Mañana'),
        ('Tarde', 'Tarde'),
        ('Noche', 'Noche')
    ], validators=[DataRequired()])
    activo = BooleanField('Activo', default=True)
    submit = SubmitField('Guardar')
