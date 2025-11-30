from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from saas.internados import bp
from saas.internados.models import Internado, Cama, Evolucion
from saas.internados.forms import InternadoForm, AltaForm, EvolucionForm, CamaForm
from saas.models import Paciente, Usuario
from saas.extensions import db, cache
from sqlalchemy.orm import joinedload
from datetime import datetime


@bp.route('/')
@login_required
def index():
    """Lista internaciones activas con ocupación de camas"""
    page = request.args.get('page', 1, type=int)
    estado_filter = request.args.get('estado', 'activo')
    sala_filter = request.args.get('sala', '')
    
    # Query base con EAGER LOADING para evitar N+1
    query = Internado.query.options(
        joinedload(Internado.paciente),
        joinedload(Internado.cama),
        joinedload(Internado.medico)  # ✅ Nombre correcto de la relación
    )
    
    # Filtros
    if estado_filter and estado_filter != 'todos':
        query = query.filter_by(estado=estado_filter)
    
    # Paginar
    pagination = query.order_by(Internado.fecha_ingreso.desc()).paginate(
        page=page, per_page=15, error_out=False
    )
    internados = pagination.items
    
    # Estadísticas de camas
    total_camas = Cama.query.count()
    camas_libres = Cama.query.filter_by(estado='libre').count()
    camas_ocupadas = Cama.query.filter_by(estado='ocupada').count()
    camas_mantenimiento = Cama.query.filter_by(estado='mantenimiento').count()
    
    # Camas por sala
    salas = db.session.query(
        Cama.sala,
        db.func.count(Cama.id).label('total'),
        db.func.sum(db.case((Cama.estado == 'libre', 1), else_=0)).label('libres')
    ).group_by(Cama.sala).all()
    
    return render_template('internados/index.html',
                          internados=internados,
                          pagination=pagination,
                          total_camas=total_camas,
                          camas_libres=camas_libres,
                          camas_ocupadas=camas_ocupadas,
                          camas_mantenimiento=camas_mantenimiento,
                          salas=salas,
                          estado_filter=estado_filter,
                          sala_filter=sala_filter)


@bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def nuevo():
    """Registrar nueva internación"""
    form = InternadoForm()
    
    # Cargar opciones de selects con CACHÉ para evitar queries repetidas
    @cache.cached(timeout=300, key_prefix='pacientes_select')
    def get_pacientes_choices():
        return [(p.id, f"{p.nombre_completo} - {p.cedula}") 
                for p in Paciente.query.order_by(Paciente.nombre).all()]
    
    @cache.cached(timeout=60, key_prefix='camas_libres_select')
    def get_camas_libres_choices():
        return [(c.id, f"{c.codigo} - {c.sala} ({c.estado})") 
                for c in Cama.query.filter_by(estado='libre').order_by(Cama.codigo).all()]
    
    @cache.cached(timeout=300, key_prefix='medicos_select')
    def get_medicos_choices():
        return [(u.id, u.nombre_completo) 
                for u in Usuario.query.filter_by(rol='medico').order_by(Usuario.nombre).all()]
    
    form.paciente_id.choices = get_pacientes_choices()
    form.cama_id.choices = get_camas_libres_choices()
    form.medico_id.choices = get_medicos_choices()
    
    if form.validate_on_submit():
        # Verificar que la cama esté libre
        cama = Cama.query.get_or_404(form.cama_id.data)
        if cama.estado != 'libre':
            flash('La cama seleccionada no está disponible', 'danger')
            return redirect(url_for('internados.nuevo'))
        
        # Crear internado
        internado = Internado(
            paciente_id=form.paciente_id.data,
            cama_id=form.cama_id.data,
            medico_id=form.medico_id.data,
            fecha_ingreso=form.fecha_ingreso.data,
            motivo=form.motivo.data,
            diagnostico_inicial=form.diagnostico_inicial.data
        )
        
        # Actualizar estado de cama
        cama.estado = 'ocupada'
        
        db.session.add(internado)
        db.session.commit()
        
        flash(f'Paciente internado en cama {cama.codigo}', 'success')
        return redirect(url_for('internados.show', id=internado.id))
    
    # Valor por defecto para fecha_ingreso
    if not form.fecha_ingreso.data:
        form.fecha_ingreso.data = datetime.utcnow()
    
    return render_template('internados/form.html', form=form, title='Nueva Internación')


@bp.route('/<int:id>')
@login_required
def show(id):
    """Detalle de internación con evoluciones"""
    internado = Internado.query.get_or_404(id)
    
    # Formularios
    alta_form = AltaForm()
    evolucion_form = EvolucionForm()
    
    # Evoluciones paginadas
    page = request.args.get('page', 1, type=int)
    pagination = internado.evoluciones.paginate(
        page=page, per_page=10, error_out=False
    )
    evoluciones = pagination.items
    
    return render_template('internados/show.html',
                          internado=internado,
                          evoluciones=evoluciones,
                          pagination=pagination,
                          alta_form=alta_form,
                          evolucion_form=evolucion_form)


@bp.route('/<int:id>/alta', methods=['POST'])
@login_required
def alta(id):
    """Dar alta a paciente internado"""
    internado = Internado.query.get_or_404(id)
    
    if internado.estado != 'activo':
        flash('Este internado ya no está activo', 'warning')
        return redirect(url_for('internados.show', id=id))
    
    form = AltaForm()
    
    if form.validate_on_submit():
        # Actualizar internado
        internado.estado = 'alta'
        internado.fecha_alta = datetime.utcnow()
        internado.tipo_alta = form.tipo_alta.data
        internado.observaciones_alta = form.observaciones_alta.data
        
        # Liberar cama
        internado.cama.estado = 'libre'
        
        db.session.commit()
        
        flash(f'Alta registrada exitosamente ({form.tipo_alta.data})', 'success')
        return redirect(url_for('internados.show', id=id))
    
    flash('Error al procesar el alta', 'danger')
    return redirect(url_for('internados.show', id=id))


@bp.route('/<int:id>/evolucion', methods=['POST'])
@login_required
def nueva_evolucion(id):
    """Registrar nueva evolución"""
    internado = Internado.query.get_or_404(id)
    
    if internado.estado != 'activo':
        flash('No se pueden agregar evoluciones a internados inactivos', 'warning')
        return redirect(url_for('internados.show', id=id))
    
    form = EvolucionForm()
    
    if form.validate_on_submit():
        evolucion = Evolucion(
            internado_id=internado.id,
            usuario_id=current_user.id,
            notas=form.notas.data,
            temperatura=form.temperatura.data,
            presion_sistolica=form.presion_sistolica.data,
            presion_diastolica=form.presion_diastolica.data,
            frecuencia_cardiaca=form.frecuencia_cardiaca.data,
            frecuencia_respiratoria=form.frecuencia_respiratoria.data,
            saturacion=form.saturacion.data
        )
        
        db.session.add(evolucion)
        db.session.commit()
        
        flash('Evolución registrada exitosamente', 'success')
        return redirect(url_for('internados.show', id=id))
    
    flash('Error al registrar evolución', 'danger')
    return redirect(url_for('internados.show', id=id))


@bp.route('/camas')
@login_required
def camas():
    """Gestión de camas"""
    page = request.args.get('page', 1, type=int)
    sala_filter = request.args.get('sala', '')
    estado_filter = request.args.get('estado', '')
    
    query = Cama.query
    
    if sala_filter:
        query = query.filter(Cama.sala.contains(sala_filter))
    
    if estado_filter:
        query = query.filter_by(estado=estado_filter)
    
    pagination = query.order_by(Cama.codigo).paginate(
        page=page, per_page=20, error_out=False
    )
    camas_list = pagination.items
    
    return render_template('internados/camas.html',
                          camas=camas_list,
                          pagination=pagination,
                          sala_filter=sala_filter,
                          estado_filter=estado_filter)


@bp.route('/camas/<int:id>/liberar', methods=['POST'])
@login_required
def liberar_cama(id):
    """Liberar cama manualmente (si no hay internado activo)"""
    cama = Cama.query.get_or_404(id)
    
    # Verificar que no haya internado activo
    internado_activo = cama.internados.filter_by(estado='activo').first()
    
    if internado_activo:
        flash('No se puede liberar la cama: hay un paciente internado', 'danger')
        return redirect(url_for('internados.camas'))
    
    cama.estado = 'libre'
    db.session.commit()
    
    flash(f'Cama {cama.codigo} liberada exitosamente', 'success')
    return redirect(url_for('internados.camas'))


@bp.route('/camas/<int:id>/mantenimiento', methods=['POST'])
@login_required
def marcar_mantenimiento(id):
    """Marcar cama en mantenimiento"""
    cama = Cama.query.get_or_404(id)
    
    # Verificar que no haya internado activo
    internado_activo = cama.internados.filter_by(estado='activo').first()
    
    if internado_activo:
        flash('No se puede poner en mantenimiento: hay un paciente internado', 'danger')
        return redirect(url_for('internados.camas'))
    
    cama.estado = 'mantenimiento'
    db.session.commit()
    
    flash(f'Cama {cama.codigo} marcada en mantenimiento', 'warning')
    return redirect(url_for('internados.camas'))
