from flask_wtf import FlaskForm
from wtforms import TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired

class OrdenLaboratorioForm(FlaskForm):
    examenes_solicitados = TextAreaField('Exámenes Solicitados', validators=[DataRequired()], render_kw={'rows': 4, 'placeholder': 'Hemograma completo\nGlicemia\nCreatinina...'})
    indicaciones = TextAreaField('Indicaciones', render_kw={'rows': 2})
    urgente = BooleanField('Urgente')
    estado = SelectField('Estado', choices=[('pendiente', 'Pendiente'), ('en_proceso', 'En Proceso'), ('completada', 'Completada')], default='pendiente')

class ResultadoForm(FlaskForm):
    examen = TextAreaField('Examen', validators=[DataRequired()])
    resultado = TextAreaField('Resultado', validators=[DataRequired()], render_kw={'rows': 3})
    valor_referencia = TextAreaField('Valor de Referencia', render_kw={'placeholder': 'Ej: 70-100 mg/dL'})
    observaciones = TextAreaField('Observaciones', render_kw={'rows': 2})
