from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime
from saas.extensions import db
from saas.models import Paciente
from sqlalchemy.orm import joinedload
from . import emergencias_bp
from .models import Emergencia
from .forms import EmergenciaForm


@emergencias_bp.route('/')
@login_required
def index():
    """
    Lista de emergencias ordenadas por nivel de triage (prioridad).
    Cola de atención: 1 (Rojo) tiene máxima prioridad.
    """
    # Filtros
    estado_filtro = request.args.get('estado', '')
    nivel_filtro = request.args.get('nivel', type=int)
    
    # Query base con EAGER LOADING para evitar N+1
    query = Emergencia.query.options(
        joinedload(Emergencia.paciente)
    )
    
    # Aplicar filtros
    if estado_filtro:
        query = query.filter_by(estado=estado_filtro)
    if nivel_filtro:
        query = query.filter_by(triage_nivel=nivel_filtro)
    
    # Ordenar por nivel de triage (1 primero) y luego por hora de ingreso
    emergencias = query.order_by(
        Emergencia.triage_nivel.asc(),
        Emergencia.hora_ingreso.asc()
    ).all()
    
    # Estadísticas
    total = len(emergencias)
    en_triaje = len([e for e in emergencias if e.estado == 'en_triaje'])
    en_atencion = len([e for e in emergencias if e.estado == 'en_atencion'])
    
    return render_template(
        'emergencias/index.html',
        emergencias=emergencias,
        estado_filtro=estado_filtro,
        nivel_filtro=nivel_filtro,
        total=total,
        en_triaje=en_triaje,
        en_atencion=en_atencion
    )


@emergencias_bp.route('/nueva', methods=['GET', 'POST'])
@login_required
def crear():
    """
    Crea nuevo registro de emergencia.
    Paciente puede buscarse por cédula en el formulario.
    """
    form = EmergenciaForm()
    paciente_id = request.args.get('paciente', type=int)
    paciente = None
    
    if paciente_id:
        paciente = Paciente.query.get_or_404(paciente_id)
    
    if form.validate_on_submit():
        if not paciente_id:
            flash('Debe buscar y seleccionar un paciente primero', 'warning')
            return render_template(
                'emergencias/form.html',
                form=form,
                paciente=None,
                titulo='Nueva Emergencia'
            )
        
        # Combinar presión sistólica/diastólica en formato string para BD
        presion_str = None
        if form.presion_sistolica.data and form.presion_diastolica.data:
            presion_str = f"{form.presion_sistolica.data}/{form.presion_diastolica.data}"
        
        # Crear emergencia con campos simplificados
        emergencia = Emergencia(
            paciente_id=paciente_id,
            tipo=form.tipo_emergencia.data,
            triage_nivel=form.nivel_triage.data,
            descripcion=form.motivo_consulta.data,
            presion_arterial=presion_str,
            frecuencia_cardiaca=form.frecuencia_cardiaca.data,
            temperatura=form.temperatura.data,
            saturacion=None,  # No se pregunta en triage inicial
            glasgow=None,  # Removido - es evaluación médica
            diagnostico_preliminar=None,  # Removido - lo hace el doctor
            observaciones=None,  # Se agrega después si es necesario
            tratamiento=None,  # Removido - lo decide el doctor
            hora_ingreso=datetime.utcnow(),
            estado='en_triaje'  # Automático
        )
        
        db.session.add(emergencia)
        db.session.commit()
        
        flash(f'Emergencia registrada - Nivel {emergencia.nombre_triage}', 'success')
        return redirect(url_for('emergencias.show', id=emergencia.id))
    
    return render_template(
        'emergencias/form.html',
        form=form,
        paciente=paciente,
        titulo='Nueva Emergencia'
    )


@emergencias_bp.route('/<int:id>')
@login_required
def show(id):
    """Muestra detalle completo de una emergencia"""
    emergencia = Emergencia.query.get_or_404(id)
    return render_template('emergencias/show.html', emergencia=emergencia)


@emergencias_bp.route('/<int:id>/estado', methods=['POST'])
@login_required
def cambiar_estado(id):
    """
    Cambia el estado de la emergencia.
    Transiciones: en_triaje -> en_atencion -> derivado/alta
    """
    emergencia = Emergencia.query.get_or_404(id)
    
    nuevo_estado = request.form.get('estado')
    tratamiento = request.form.get('tratamiento', '')
    observaciones = request.form.get('observaciones', '')
    
    if nuevo_estado not in ['en_triaje', 'en_atencion', 'derivado', 'alta']:
        flash('Estado inválido', 'danger')
        return redirect(url_for('emergencias.show', id=id))
    
    # Actualizar estado
    estado_anterior = emergencia.estado
    emergencia.estado = nuevo_estado
    
    # Registrar hora de atención si pasa a en_atencion
    if nuevo_estado == 'en_atencion' and not emergencia.hora_atencion:
        emergencia.hora_atencion = datetime.utcnow()
        emergencia.atendido_por = current_user.id
    
    # Registrar hora de alta si se da de alta
    if nuevo_estado == 'alta' and not emergencia.hora_alta:
        emergencia.hora_alta = datetime.utcnow()
    
    # Actualizar tratamiento y observaciones
    if tratamiento:
        if emergencia.tratamiento:
            emergencia.tratamiento += f"\n\n[{datetime.utcnow().strftime('%Y-%m-%d %H:%M')}]\n{tratamiento}"
        else:
            emergencia.tratamiento = tratamiento
    
    if observaciones:
        if emergencia.observaciones:
            emergencia.observaciones += f"\n\n[{datetime.utcnow().strftime('%Y-%m-%d %H:%M')}]\n{observaciones}"
        else:
            emergencia.observaciones = observaciones
    
    emergencia.updated_at = datetime.utcnow()
    db.session.commit()
    
    flash(f'Estado cambiado de "{estado_anterior}" a "{nuevo_estado}"', 'success')
    return redirect(url_for('emergencias.show', id=id))
