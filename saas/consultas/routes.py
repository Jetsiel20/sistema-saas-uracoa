
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime, date
from saas.extensions import db, cache
from saas.models import Paciente
from sqlalchemy.orm import joinedload
from . import consultas_bp
from .models import Consulta
from .forms import ConsultaForm


# Registrar consulta diaria (vista simplificada, profesional y segura)
@consultas_bp.route('/registrar', methods=['GET', 'POST'])
@login_required
def registrar_consulta():
    form = ConsultaForm()
    hoy = date.today()

    def obtener_consultas_hoy():
        return Consulta.query.filter(
            db.func.date(Consulta.fecha_hora) == hoy
        ).order_by(Consulta.fecha_hora.asc()).all()

    consultas_hoy = obtener_consultas_hoy()

    if form.validate_on_submit():
        paciente = Paciente.query.get(form.paciente_id.data)

        if not paciente:
            flash("Paciente no válido", "danger")
            return render_template(
                'consultas_form.html',
                form=form,
                consultas_hoy=consultas_hoy
            )

        consulta = Consulta(
            paciente_id=paciente.id,
            medico_id=current_user.id,
            fecha_hora=datetime.utcnow(),
            motivo=form.motivo.data,
            temperatura=form.temperatura.data,
            presion_sistolica=form.presion_sistolica.data,
            presion_diastolica=form.presion_diastolica.data,
            frecuencia_cardiaca=form.frecuencia_cardiaca.data,
            peso=form.peso.data,
            altura=form.altura.data,
            turno=form.turno.data,
            estado=form.estado.data
        )

        # Lógica existente del sistema
        consulta.asignar_turno_y_numero()
        consulta.validar_antes_guardar()

        db.session.add(consulta)
        db.session.commit()

        flash("✅ Consulta registrada correctamente", "success")

        # Volver a cargar la lista de consultas del día
        consultas_hoy = obtener_consultas_hoy()

    return render_template(
        'consultas_form.html',
        form=form,
        consultas_hoy=consultas_hoy
    )
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from datetime import datetime, date
from saas.extensions import db, cache
from saas.models import Paciente
from sqlalchemy.orm import joinedload
from . import consultas_bp
from .models import Consulta
from .forms import ConsultaForm


@consultas_bp.route('/')
@login_required
def index():
    """
    Lista consultas del día con filtros por paciente, médico, turno y estado.
    Ahora, por defecto, siempre muestra las consultas del día actual del usuario logueado (o todas si es admin).
    """
    # Obtener parámetros de filtro
    paciente_query = request.args.get('paciente', '', type=str)
    medico_id = request.args.get('medico', None, type=int)
    estado = request.args.get('estado', '', type=str)
    sector = request.args.get('sector', '', type=str)
    turno = request.args.get('turno', '', type=str)
    fecha = request.args.get('fecha', None, type=str)

    # Si el filtro de fecha está vacío, siempre mostrar las consultas del día actual
    if not fecha:
        fecha = date.today().isoformat()

    # Query base con EAGER LOADING para evitar N+1
    query = Consulta.query.options(
        joinedload(Consulta.paciente),
        joinedload(Consulta.medico)
    )

    # Filtro por fecha (solo del día seleccionado)
    if fecha:
        try:
            fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
            query = query.filter(db.func.date(Consulta.fecha_hora) == fecha_obj)
        except ValueError:
            pass

    # Filtro por turno
    if turno:
        query = query.filter_by(turno=turno)

    # Filtro por paciente (búsqueda por nombre o cédula)
    if paciente_query:
        query = query.join(Paciente).filter(
            db.or_(
                Paciente.nombre.ilike(f'%{paciente_query}%'),
                Paciente.apellido.ilike(f'%{paciente_query}%'),
                Paciente.cedula.ilike(f'%{paciente_query}%')
            )
        )

    # Filtro por médico
    if medico_id:
        query = query.filter_by(medico_id=medico_id)
    elif not current_user.es_admin:
        # Si no es admin, solo ver sus propias consultas
        query = query.filter_by(medico_id=current_user.id)

    # Filtro por estado
    if estado:
        query = query.filter_by(estado=estado)

    # Filtro por sector
    if sector:
        query = query.filter(Consulta.sector.ilike(f'%{sector}%'))

    # Ordenar y paginar
    page = request.args.get('page', 1, type=int)
    per_page = 20

    pagination = query.order_by(Consulta.fecha_hora.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    consultas = pagination.items

    # Obtener lista de médicos para el filtro (CACHEADA)
    @cache.cached(timeout=300, key_prefix='medicos_activos')
    def get_medicos_activos():
        from saas.models import Usuario
        return Usuario.query.filter_by(
            rol='medico',
            activo=True
        ).all()

    medicos = get_medicos_activos()

    return render_template(
        'index.html',
        consultas=consultas,
        pagination=pagination,
        medicos=medicos,
        filtros={
            'paciente': paciente_query,
            'medico': medico_id,
            'estado': estado,
            'sector': sector,
            'turno': turno,
            'fecha': fecha
        }
    )


@consultas_bp.route('/nueva', methods=['GET', 'POST'])
@login_required
def crear():
    """
    Crea nueva consulta con selector de pacientes y control de turnos.
    Sistema de turnos: 20 consultas máximo por turno (mañana 07:00-12:00 / tarde 13:30-17:00)
    """
    form = ConsultaForm()
    
    # Verificar disponibilidad del turno actual
    turno_info = {
        'turno': None,
        'disponible': False,
        'consultas_actuales': 0,
        'limite': 20,
        'error_mensaje': None
    }
    
    try:
        turno_actual = Consulta.detectar_turno_actual()
        disponible, count, limite = Consulta.verificar_disponibilidad_turno(turno_actual)
        turno_info.update({
            'turno': turno_actual,
            'disponible': disponible,
            'consultas_actuales': count,
            'limite': limite
        })
    except ValueError as e:
        turno_info['error_mensaje'] = str(e)
    
    # TODO MEJORAS: Diagnóstico y tratamiento se completarán en módulo médico
    
    # Ya no necesitamos poblar choices (viene de búsqueda AJAX)
    # Validación de paciente_id se hace en el backend al submit
    
    if form.validate_on_submit():
        # Verificar que el paciente existe y está activo
        try:
            paciente_id = int(form.paciente_id.data)
        except (ValueError, TypeError):
            flash('❌ Debe buscar y seleccionar un paciente válido', 'danger')
            return render_template('form.html', form=form, titulo='Nueva Consulta', 
                                   turno_info=turno_info)
        
        paciente = Paciente.query.get(paciente_id)
        if not paciente or not paciente.activo:
            flash('❌ El paciente seleccionado no existe o está inactivo', 'danger')
            return render_template('form.html', form=form, titulo='Nueva Consulta', 
                                   turno_info=turno_info)
        
        # Verificar disponibilidad nuevamente antes de crear
        try:
            turno_actual = Consulta.detectar_turno_actual()
            disponible, count, limite = Consulta.verificar_disponibilidad_turno(turno_actual)
            
            if not disponible:
                flash(f'❌ Límite de {limite} consultas alcanzado para el turno de {turno_actual}. '
                      f'Por favor, intente en el próximo turno.', 'danger')
                return render_template('form.html', form=form, titulo='Nueva Consulta', 
                                       turno_info=turno_info)
        except ValueError as e:
            flash(f'❌ {str(e)}', 'danger')
            return render_template('form.html', form=form, titulo='Nueva Consulta', 
                                   turno_info=turno_info)
        
        consulta = Consulta(
            paciente_id=paciente_id,
            medico_id=current_user.id,
            fecha_hora=datetime.utcnow(),
            motivo=form.motivo.data,
            temperatura=form.temperatura.data,
            presion_sistolica=form.presion_sistolica.data,
            presion_diastolica=form.presion_diastolica.data,
            frecuencia_cardiaca=form.frecuencia_cardiaca.data,
            peso=form.peso.data,
            altura=form.altura.data,
            sector=form.sector.data,
            nivel_conciencia=form.nivel_conciencia.data if form.nivel_conciencia.data else None,
            estado='abierta'
        )
        
        # Asignar turno y número de consulta automáticamente
        try:
            consulta.asignar_turno_y_numero()
        except ValueError as e:
            flash(f'❌ {str(e)}', 'danger')
            return render_template('form.html', form=form, titulo='Nueva Consulta', 
                                   turno_info=turno_info)
        
        # Validar antes de guardar
        try:
            consulta.validar_antes_guardar()
        except ValueError as e:
            flash(f'Error de validación: {str(e)}', 'danger')
            return render_template('form.html', form=form, titulo='Nueva Consulta', 
                                   turno_info=turno_info)
        
        db.session.add(consulta)
        db.session.commit()
        
        # Flash con información del turno y alertas
        mensaje_turno = f'✅ Consulta #{consulta.numero_consulta} registrada en turno de {consulta.turno}.'
        
        if consulta.alerta_riesgo:
            flash(f'{mensaje_turno} ⚠️ ATENCIÓN: Se detectaron signos vitales fuera de rango normal.', 'warning')
        else:
            flash(mensaje_turno, 'success')
        
        return redirect(url_for('consultas.show', id=consulta.id))
    
    return render_template(
        'form.html',
        form=form,
        titulo='Nueva Consulta',
        turno_info=turno_info
    )


@consultas_bp.route('/<int:id>')
@login_required
def show(id):
    """
    Muestra detalle de una consulta con alertas y recomendaciones.
    """
    consulta = Consulta.query.get_or_404(id)
    
    # Verificar permisos: solo el médico que la creó o admin
    if not current_user.es_admin and consulta.medico_id != current_user.id:
        flash('No tienes permiso para ver esta consulta', 'danger')
        return redirect(url_for('consultas.index'))
    
    return render_template('show.html', consulta=consulta)


@consultas_bp.route('/<int:id>/cerrar', methods=['POST'])
@login_required
def cerrar(id):
    """
    Cambia el estado de la consulta a 'cerrada'.
    """
    consulta = Consulta.query.get_or_404(id)
    
    # Verificar permisos
    if not current_user.es_admin and consulta.medico_id != current_user.id:
        flash('No tienes permiso para cerrar esta consulta', 'danger')
        return redirect(url_for('consultas.index'))
    
    if consulta.estado == 'cerrada':
        flash('La consulta ya está cerrada', 'info')
    else:
        consulta.estado = 'cerrada'
        consulta.fecha_cierre = datetime.utcnow()
        db.session.commit()
        flash('Consulta cerrada exitosamente', 'success')
    
    return redirect(url_for('consultas.show', id=consulta.id))
