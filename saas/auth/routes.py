"""
Rutas de Autenticación
Hospital Tipo 1 Uracoa - J&S Software Inteligentes
"""
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from datetime import datetime
from saas.auth import auth_bp
from saas.auth.forms import LoginForm, RegistroForm, CambiarPasswordForm
from saas.models import Usuario
from saas.extensions import db


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Página de inicio de sesión"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        usuario = Usuario.query.filter_by(username=form.username.data).first()
        
        if usuario is None or not usuario.check_password(form.password.data):
            flash('Usuario o contraseña incorrectos', 'danger')
            return redirect(url_for('auth.login'))
        
        if not usuario.activo:
            flash('Tu cuenta está inactiva. Contacta al administrador.', 'warning')
            return redirect(url_for('auth.login'))
        
        login_user(usuario, remember=form.remember_me.data)
        usuario.ultimo_acceso = datetime.utcnow()
        db.session.commit()
        
        flash(f'Bienvenido, {usuario.nombre_completo}!', 'success')
        
        # Redireccionar a la página solicitada o al dashboard
        next_page = request.args.get('next')
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('main.dashboard')
        return redirect(next_page)
    
    return render_template('auth/login.html', form=form)


@auth_bp.route('/registro', methods=['GET', 'POST'])
@login_required
def registro():
    """Página de registro de usuarios (solo para admins)"""
    if not current_user.es_admin:
        flash('No tienes permisos para acceder a esta página.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    form = RegistroForm()
    
    # Debug: mostrar datos recibidos en POST
    if request.method == 'POST':
        print("=== DATOS RECIBIDOS EN POST ===")
        print(f"Username: {form.username.data}")
        print(f"Email: {form.email.data}")
        print(f"Nombre: {form.nombre.data}")
        print(f"Apellido: {form.apellido.data}")
        print(f"Cedula: {form.cedula.data}")
        print(f"Password: {'***' if form.password.data else 'VACIO'}")
        print(f"Rol: {form.rol.data}")
        print(f"Especialidad: {form.especialidad.data}")
        
    if form.validate_on_submit():
        try:
            usuario = Usuario(
                username=form.username.data,
                email=form.email.data,
                nombre=form.nombre.data,
                apellido=form.apellido.data,
                cedula=form.cedula.data,
                telefono=form.telefono.data,
                rol=form.rol.data,
                especialidad=form.especialidad.data if form.especialidad.data else None,
                codigo_profesional=form.codigo_profesional.data if form.codigo_profesional.data else None
            )
            usuario.set_password(form.password.data)
            
            db.session.add(usuario)
            db.session.commit()
            
            flash(f'Doctor {usuario.nombre_completo} registrado exitosamente!', 'success')
            return redirect(url_for('main.usuarios'))
        except Exception as e:
            db.session.rollback()
            print(f"ERROR AL GUARDAR: {str(e)}")
            flash(f'Error al registrar: {str(e)}', 'danger')
    else:
        # Mostrar errores de validación
        if request.method == 'POST':
            print("=== ERRORES DE VALIDACIÓN ===")
            for field, errors in form.errors.items():
                print(f"{field}: {errors}")
                for error in errors:
                    flash(f'{field}: {error}', 'danger')
    
    return render_template('auth/registro.html', form=form)


@auth_bp.route('/logout')
@login_required
def logout():
    """Cerrar sesión"""
    logout_user()
    flash('Has cerrado sesión exitosamente.', 'info')
    return redirect(url_for('auth.login'))


@auth_bp.route('/perfil')
@login_required
def perfil():
    """Ver perfil del usuario"""
    return render_template('auth/perfil.html', usuario=current_user)


@auth_bp.route('/cambiar-password', methods=['GET', 'POST'])
@login_required
def cambiar_password():
    """Cambiar contraseña del usuario"""
    form = CambiarPasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.password_actual.data):
            flash('La contraseña actual es incorrecta.', 'danger')
            return redirect(url_for('auth.cambiar_password'))
        
        current_user.set_password(form.password_nueva.data)
        db.session.commit()
        
        flash('Contraseña cambiada exitosamente!', 'success')
        return redirect(url_for('auth.perfil'))
    
    return render_template('auth/cambiar_password.html', form=form)
