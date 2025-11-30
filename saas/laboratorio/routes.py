from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from saas.extensions import db
from saas.models import Paciente
from sqlalchemy.orm import joinedload
from . import laboratorio_bp
from .models import OrdenLaboratorio, ResultadoLaboratorio
from .forms import OrdenLaboratorioForm, ResultadoForm

@laboratorio_bp.route('/')
@login_required
def index():
    page = request.args.get('page', 1, type=int)
    estado = request.args.get('estado', 'todas')
    
    # Query con EAGER LOADING para evitar N+1
    query = OrdenLaboratorio.query.options(
        joinedload(OrdenLaboratorio.paciente),
        joinedload(OrdenLaboratorio.medico)
    ).order_by(OrdenLaboratorio.fecha_orden.desc())
    
    if estado != 'todas':
        query = query.filter_by(estado=estado)
    pagination = query.paginate(page=page, per_page=20, error_out=False)
    return render_template('laboratorio/index.html', ordenes=pagination.items, pagination=pagination, estado_filtro=estado)

@laboratorio_bp.route('/nueva/<int:paciente_id>', methods=['GET', 'POST'])
@login_required
def crear(paciente_id):
    paciente = Paciente.query.get_or_404(paciente_id)
    form = OrdenLaboratorioForm()
    if form.validate_on_submit():
        orden = OrdenLaboratorio(paciente_id=paciente.id, medico_id=current_user.id, examenes_solicitados=form.examenes_solicitados.data, indicaciones=form.indicaciones.data, urgente=form.urgente.data, estado=form.estado.data)
        orden.generar_codigo()
        db.session.add(orden)
        db.session.commit()
        flash(f'Orden {orden.codigo_orden} creada', 'success')
        return redirect(url_for('laboratorio.show', id=orden.id))
    return render_template('laboratorio/form.html', form=form, paciente=paciente, titulo='Nueva Orden')

@laboratorio_bp.route('/<int:id>')
@login_required
def show(id):
    orden = OrdenLaboratorio.query.get_or_404(id)
    return render_template('laboratorio/show.html', orden=orden)

@laboratorio_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    orden = OrdenLaboratorio.query.get_or_404(id)
    form = OrdenLaboratorioForm(obj=orden)
    if form.validate_on_submit():
        form.populate_obj(orden)
        if form.estado.data == 'completada' and not orden.fecha_resultado:
            from datetime import datetime
            orden.fecha_resultado = datetime.utcnow()
        db.session.commit()
        flash('Orden actualizada', 'success')
        return redirect(url_for('laboratorio.show', id=orden.id))
    return render_template('laboratorio/form.html', form=form, paciente=orden.paciente, orden=orden, titulo='Editar Orden')
