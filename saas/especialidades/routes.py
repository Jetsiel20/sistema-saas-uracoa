from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required
from saas.extensions import db, cache
from . import especialidades_bp
from .models import Especialidad
from .forms import EspecialidadForm

@especialidades_bp.route('/')
@login_required
def index():
    """Listar especialidades - OPTIMIZADA con paginación"""
    page = request.args.get('page', 1, type=int)
    
    # Paginación directa sin caché (objeto Pagination no serializable)
    especialidades = Especialidad.query.filter_by(activo=True).order_by(
        Especialidad.nombre_medico
    ).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('especialidades/index.html', especialidades=especialidades)

@especialidades_bp.route('/nueva', methods=['GET', 'POST'])
@login_required
def crear():
    form = EspecialidadForm()
    if form.validate_on_submit():
        especialidad = Especialidad(
            nombre_medico=form.nombre_medico.data,
            especialidad=form.especialidad.data,
            telefono_contacto=form.telefono_contacto.data,
            turno=form.turno.data,
            activo=form.activo.data
        )
        db.session.add(especialidad)
        db.session.commit()
        flash('Especialidad registrada exitosamente.', 'success')
        return redirect(url_for('especialidades.index'))
    return render_template('especialidades/form.html', form=form, modo='Nueva')

@especialidades_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    especialidad = Especialidad.query.get_or_404(id)
    form = EspecialidadForm(obj=especialidad)
    if form.validate_on_submit():
        form.populate_obj(especialidad)
        db.session.commit()
        flash('Registro actualizado correctamente.', 'info')
        return redirect(url_for('especialidades.index'))
    return render_template('especialidades/form.html', form=form, modo='Editar')

@especialidades_bp.route('/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar(id):
    especialidad = Especialidad.query.get_or_404(id)
    especialidad.activo = False
    db.session.commit()
    flash('Especialidad desactivada correctamente.', 'warning')
    return redirect(url_for('especialidades.index'))
