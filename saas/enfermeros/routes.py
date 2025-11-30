from flask import render_template, redirect, url_for, flash
from flask_login import login_required
from saas.models import Usuario
from . import enfermeros_bp


@enfermeros_bp.route('/')
@login_required
def index():
    """Lista de enfermeros del hospital"""
    enfermeros = Usuario.query.filter_by(rol='enfermera', activo=True).all()
    return render_template('enfermeros/index.html', enfermeros=enfermeros)


@enfermeros_bp.route('/turnos')
@login_required
def turnos():
    """Gestión de turnos de enfermeros"""
    flash('Módulo de turnos en desarrollo', 'info')
    return redirect(url_for('enfermeros.index'))
