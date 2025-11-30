"""
Formularios de Autenticación
Hospital Tipo 1 Uracoa - J&S Software Inteligentes
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError
from saas.models import Usuario


class LoginForm(FlaskForm):
    """Formulario de inicio de sesión"""
    username = StringField('Usuario', validators=[
        DataRequired(message='El usuario es requerido'),
        Length(min=3, max=80, message='El usuario debe tener entre 3 y 80 caracteres')
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es requerida')
    ])
    remember_me = BooleanField('Recordarme')
    submit = SubmitField('Iniciar Sesión')


class RegistroForm(FlaskForm):
    """Formulario de registro de usuario"""
    username = StringField('Usuario', validators=[
        DataRequired(message='El usuario es requerido'),
        Length(min=3, max=80, message='El usuario debe tener entre 3 y 80 caracteres')
    ])
    email = StringField('Email', validators=[
        DataRequired(message='El email es requerido'),
        Email(message='Email inválido')
    ])
    nombre = StringField('Nombre', validators=[
        DataRequired(message='El nombre es requerido'),
        Length(min=2, max=100)
    ])
    apellido = StringField('Apellido', validators=[
        DataRequired(message='El apellido es requerido'),
        Length(min=2, max=100)
    ])
    cedula = StringField('Cédula', validators=[
        DataRequired(message='La cédula es requerida'),
        Length(min=6, max=20)
    ])
    telefono = StringField('Teléfono', validators=[
        Length(max=20)
    ])
    rol = SelectField('Rol', choices=[
        ('medico', 'Médico'),
        ('enfermera', 'Enfermera'),
        ('recepcionista', 'Recepcionista'),
        ('farmacia', 'Farmacia'),
        ('laboratorio', 'Laboratorio'),
        ('admin', 'Administrador')
    ], validators=[DataRequired()])
    especialidad = StringField('Especialidad (opcional)', validators=[Length(max=100)])
    codigo_profesional = StringField('Código Profesional (opcional)', validators=[Length(max=50)])
    
    password = PasswordField('Contraseña', validators=[
        Length(min=6, message='La contraseña debe tener al menos 6 caracteres')
    ])
    password2 = PasswordField('Confirmar Contraseña', validators=[
        EqualTo('password', message='Las contraseñas no coinciden')
    ])
    submit = SubmitField('Registrar')
    
    def validate_username(self, username):
        """Validar que el usuario no exista"""
        usuario = Usuario.query.filter_by(username=username.data).first()
        if usuario:
            raise ValidationError('Este usuario ya está registrado.')
    
    def validate_email(self, email):
        """Validar que el email no exista"""
        usuario = Usuario.query.filter_by(email=email.data).first()
        if usuario:
            raise ValidationError('Este email ya está registrado.')
    
    def validate_cedula(self, cedula):
        """Validar que la cédula no exista"""
        usuario = Usuario.query.filter_by(cedula=cedula.data).first()
        if usuario:
            raise ValidationError('Esta cédula ya está registrada.')


class CambiarPasswordForm(FlaskForm):
    """Formulario para cambiar contraseña"""
    password_actual = PasswordField('Contraseña Actual', validators=[
        DataRequired(message='La contraseña actual es requerida')
    ])
    password_nueva = PasswordField('Nueva Contraseña', validators=[
        DataRequired(message='La nueva contraseña es requerida'),
        Length(min=6, message='La contraseña debe tener al menos 6 caracteres')
    ])
    password_nueva2 = PasswordField('Confirmar Nueva Contraseña', validators=[
        DataRequired(message='Confirma tu nueva contraseña'),
        EqualTo('password_nueva', message='Las contraseñas no coinciden')
    ])
    submit = SubmitField('Cambiar Contraseña')
