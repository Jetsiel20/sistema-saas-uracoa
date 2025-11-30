"""
Formularios del módulo Medicamentos
Inventario institucional sin funciones comerciales
"""
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, IntegerField, SelectField, DateField
from wtforms.validators import DataRequired, Optional, NumberRange

class MedicamentoForm(FlaskForm):
    """Formulario para registro de medicamentos en inventario"""
    
    # Información básica
    nombre = StringField(
        'Nombre Comercial',
        validators=[DataRequired(message='El nombre es obligatorio')],
        render_kw={'placeholder': 'Ej: Paracetamol'}
    )
    nombre_generico = StringField(
        'Nombre Genérico',
        validators=[Optional()],
        render_kw={'placeholder': 'Ej: Acetaminofén'}
    )
    presentacion = SelectField(
        'Presentación',
        choices=[
            ('', 'Seleccione...'),
            ('tabletas', 'Tabletas'),
            ('capsulas', 'Cápsulas'),
            ('jarabe', 'Jarabe'),
            ('suspension', 'Suspensión'),
            ('inyectable', 'Inyectable'),
            ('crema', 'Crema/Pomada'),
            ('gotas', 'Gotas'),
            ('spray', 'Spray'),
            ('supositorio', 'Supositorio'),
            ('otro', 'Otro')
        ],
        validators=[Optional()]
    )
    concentracion = StringField(
        'Concentración',
        validators=[Optional()],
        render_kw={'placeholder': 'Ej: 500mg, 120mg/5ml'}
    )
    
    # Registro
    codigo_barras = StringField(
        'Código de Barras',
        validators=[Optional()],
        render_kw={'placeholder': 'Código de barras (opcional)'}
    )
    registro_sanitario = StringField(
        'Registro Sanitario',
        validators=[Optional()],
        render_kw={'placeholder': 'Número de registro'}
    )
    laboratorio = StringField(
        'Laboratorio',
        validators=[Optional()],
        render_kw={'placeholder': 'Fabricante o laboratorio'}
    )
    
    # Inventario
    cantidad_stock = IntegerField(
        'Cantidad Disponible',
        validators=[DataRequired(), NumberRange(min=0)],
        default=0,
        render_kw={'placeholder': '0'}
    )
    unidad_medida = SelectField(
        'Unidad de Medida',
        choices=[
            ('unidades', 'Unidades'),
            ('cajas', 'Cajas'),
            ('frascos', 'Frascos'),
            ('ampolletas', 'Ampolletas'),
            ('blister', 'Blister'),
            ('otro', 'Otro')
        ],
        default='unidades'
    )
    stock_minimo = IntegerField(
        'Stock Mínimo (Alerta)',
        validators=[Optional(), NumberRange(min=0)],
        default=10,
        render_kw={'placeholder': '10'}
    )
    
    # Vencimiento
    fecha_vencimiento = DateField(
        'Fecha de Vencimiento',
        validators=[Optional()],
        format='%Y-%m-%d'
    )
    
    # Control
    requiere_receta = SelectField(
        'Requiere Receta',
        choices=[
            ('1', 'Sí'),
            ('0', 'No')
        ],
        default='1',
        coerce=int
    )
    
    observaciones = TextAreaField(
        'Observaciones',
        validators=[Optional()],
        render_kw={'rows': 3, 'placeholder': 'Notas adicionales sobre el medicamento...'}
    )
