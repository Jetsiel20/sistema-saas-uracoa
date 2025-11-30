"""
Rutas Principales del Sistema
Hospital Tipo 1 Uracoa - J&S Software Inteligentes
"""
from flask import render_template, redirect, url_for, flash, request, jsonify
from flask_login import login_required, current_user
from datetime import datetime, timedelta
from sqlalchemy import func, or_
from sqlalchemy.orm import joinedload
from saas.main import main_bp
from saas.main.forms import PacienteForm, CitaForm, HistoriaClinicaForm
from saas.models import Usuario, Paciente, Cita, HistoriaClinica, Medicamento
from saas.extensions import db, cache


@main_bp.route('/')
def index():
    """Página de inicio"""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))


@main_bp.route('/dashboard')
@login_required
def dashboard():
    """Dashboard principal del sistema con caché para estadísticas"""
    
    # Función para obtener estadísticas (cacheadas)
    @cache.cached(timeout=300, key_prefix='dashboard_stats')
    def get_statistics():
        total_pacientes = Paciente.query.filter_by(activo=True).count()
        total_usuarios = Usuario.query.filter_by(activo=True).count()
        
        hoy = datetime.now().date()
        citas_hoy = Cita.query.filter(
            func.date(Cita.fecha_hora) == hoy
        ).count()
        
        return {
            'total_pacientes': total_pacientes,
            'total_usuarios': total_usuarios,
            'citas_hoy': citas_hoy
        }
    
    stats = get_statistics()
    
    # Próximas citas (siguientes 7 días) con eager loading - NO cacheadas
    fecha_limite = datetime.now() + timedelta(days=7)
    proximas_citas = Cita.query.options(
        joinedload(Cita.paciente),
        joinedload(Cita.medico)
    ).filter(
        Cita.fecha_hora >= datetime.now(),
        Cita.fecha_hora <= fecha_limite,
        Cita.estado.in_(['programada', 'confirmada'])
    ).order_by(Cita.fecha_hora).limit(10).all()
    
    # Medicamentos con stock bajo - cacheados
    @cache.cached(timeout=300, key_prefix='medicamentos_bajo_stock')
    def get_low_stock_meds():
        return Medicamento.query.filter(
            Medicamento.cantidad_stock <= Medicamento.stock_minimo,
            Medicamento.activo == True
        ).limit(5).all()
    
    medicamentos_bajo_stock = get_low_stock_meds()
    
    # Estadísticas por rol - NO cacheadas (personalizadas por usuario)
    if current_user.es_medico:
        hoy = datetime.now().date()
        mis_citas_hoy = Cita.query.filter(
            func.date(Cita.fecha_hora) == hoy,
            Cita.medico_id == current_user.id
        ).count()
        
        mis_pacientes = Paciente.query.filter_by(
            medico_id=current_user.id,
            activo=True
        ).count()
    else:
        mis_citas_hoy = 0
        mis_pacientes = 0
    
    return render_template('main/dashboard.html',
                         total_pacientes=stats['total_pacientes'],
                         total_usuarios=stats['total_usuarios'],
                         citas_hoy=stats['citas_hoy'],
                         proximas_citas=proximas_citas,
                         medicamentos_bajo_stock=medicamentos_bajo_stock,
                         mis_citas_hoy=mis_citas_hoy,
                         mis_pacientes=mis_pacientes)


@main_bp.route('/usuarios')
@login_required
def usuarios():
    """Listar usuarios del sistema"""
    if not current_user.es_admin:
        flash('No tienes permisos para acceder a esta página.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    page = request.args.get('page', 1, type=int)
    usuarios = Usuario.query.order_by(Usuario.fecha_registro.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('main/usuarios.html', usuarios=usuarios)


@main_bp.route('/pacientes')
@login_required
def pacientes():
    """Listar pacientes - OPTIMIZADA con caché y eager loading"""
    page = request.args.get('page', 1, type=int)
    search = request.args.get('search', '', type=str)
    
    # Query con eager loading del médico tratante
    query = Paciente.query.options(joinedload(Paciente.medico_tratante))
    
    if search:
        query = query.filter(
            or_(
                Paciente.nombre.ilike(f'%{search}%'),
                Paciente.apellido.ilike(f'%{search}%'),
                Paciente.cedula.ilike(f'%{search}%')
            )
        )
    
    # Si es médico, mostrar solo sus pacientes
    if current_user.es_medico and not current_user.es_admin:
        query = query.filter_by(medico_id=current_user.id)
    
    # Cachear conteo solo si no hay búsqueda
    if not search:
        cache_key = f'pacientes_count_{current_user.id}_{current_user.rol}'
        total_count = cache.get(cache_key)
        if total_count is None:
            total_count = query.filter_by(activo=True).count()
            cache.set(cache_key, total_count, timeout=300)
    
    pacientes = query.filter_by(activo=True).order_by(
        Paciente.fecha_registro.desc()
    ).paginate(page=page, per_page=20, error_out=False)
    
    return render_template('main/pacientes.html', pacientes=pacientes, search=search)


@main_bp.route('/pacientes/<int:id>')
@login_required
def paciente_detalle(id):
    """Ver detalle de un paciente"""
    paciente = Paciente.query.get_or_404(id)
    
    # Verificar permisos
    if current_user.es_medico and not current_user.es_admin:
        if paciente.medico_id != current_user.id:
            flash('No tienes permisos para ver este paciente.', 'danger')
            return redirect(url_for('main.pacientes'))
    
    # Obtener historial de citas (query directa por lazy='select')
    citas = Cita.query.filter_by(paciente_id=paciente.id).order_by(
        Cita.fecha_hora.desc()
    ).limit(10).all()
    
    # Obtener historias clínicas (query directa por lazy='select')
    historias = HistoriaClinica.query.filter_by(paciente_id=paciente.id).order_by(
        HistoriaClinica.fecha_consulta.desc()
    ).limit(10).all()
    
    return render_template('main/paciente_detalle.html',
                         paciente=paciente,
                         citas=citas,
                         historias=historias)


@main_bp.route('/citas')
@login_required
def citas():
    """Listar citas"""
    page = request.args.get('page', 1, type=int)
    fecha = request.args.get('fecha', None, type=str)
    estado = request.args.get('estado', None, type=str)
    
    query = Cita.query.options(
        joinedload(Cita.paciente),
        joinedload(Cita.medico)
    )
    
    # Filtrar por médico si no es admin
    if current_user.es_medico and not current_user.es_admin:
        query = query.filter_by(medico_id=current_user.id)
    
    # Filtrar por fecha
    if fecha:
        try:
            fecha_obj = datetime.strptime(fecha, '%Y-%m-%d').date()
            query = query.filter(func.date(Cita.fecha_hora) == fecha_obj)
        except ValueError:
            pass
    
    # Filtrar por estado
    if estado:
        query = query.filter_by(estado=estado)
    
    citas = query.order_by(Cita.fecha_hora.desc()).paginate(
        page=page, per_page=20, error_out=False
    )
    
    return render_template('main/citas.html', citas=citas, fecha=fecha, estado=estado)


@main_bp.route('/reportes')
@login_required
def reportes():
    """Página de reportes"""
    if not current_user.es_admin:
        flash('No tienes permisos para acceder a esta página.', 'danger')
        return redirect(url_for('main.dashboard'))
    
    return render_template('main/reportes.html')


@main_bp.route('/api/estadisticas')
@login_required
def api_estadisticas():
    """API para obtener estadísticas"""
    # Pacientes por mes (últimos 6 meses)
    pacientes_por_mes = db.session.query(
        func.strftime('%Y-%m', Paciente.fecha_registro).label('mes'),
        func.count(Paciente.id).label('total')
    ).group_by('mes').order_by('mes').limit(6).all()
    
    # Citas por estado
    citas_por_estado = db.session.query(
        Cita.estado,
        func.count(Cita.id).label('total')
    ).group_by(Cita.estado).all()
    
    return jsonify({
        'pacientes_por_mes': [{'mes': m, 'total': t} for m, t in pacientes_por_mes],
        'citas_por_estado': [{'estado': e, 'total': t} for e, t in citas_por_estado]
    })


@main_bp.route('/api/pacientes/buscar')
@login_required
def api_buscar_paciente():
    """
    Búsqueda de paciente por cédula para AJAX (Consultas) - OPTIMIZADA
    
    Query params:
        cedula: Cédula del paciente (mínimo 4 caracteres)
    
    Returns:
        JSON con paciente encontrado o lista de similares
    """
    cedula = (request.args.get('cedula') or '').strip()
    
    # Validación básica
    if not cedula or len(cedula) < 4:
        return jsonify({
            "ok": False, 
            "error": "Ingrese al menos 4 dígitos de la cédula"
        }), 400
    
    # Búsqueda exacta (case-insensitive) - solo campos necesarios
    paciente = Paciente.query.filter(
        func.lower(Paciente.cedula) == cedula.lower()
    ).first()
    
    if not paciente:
        # No encontrado - buscar similares (máximo 5, solo campos básicos)
        similares = Paciente.query.with_entities(
            Paciente.id,
            Paciente.cedula,
            Paciente.nombre,
            Paciente.apellido,
            Paciente.fecha_nacimiento
        ).filter(
            Paciente.cedula.ilike(f"%{cedula}%"),
            Paciente.activo == True
        ).limit(5).all()
        
        return jsonify({
            "ok": True,
            "found": False,
            "similares": [{
                "id": p.id,
                "cedula": p.cedula,
                "nombre_completo": f"{p.nombre} {p.apellido}",
                "edad": (datetime.now().date().year - p.fecha_nacimiento.year - 
                        ((datetime.now().date().month, datetime.now().date().day) < 
                         (p.fecha_nacimiento.month, p.fecha_nacimiento.day))) if p.fecha_nacimiento else None
            } for p in similares]
        }), 200
    
    # Paciente encontrado - datos básicos
    data = {
        "id": paciente.id,
        "cedula": paciente.cedula,
        "nombre": paciente.nombre,
        "apellido": paciente.apellido,
        "nombre_completo": paciente.nombre_completo,
        "fecha_nacimiento": paciente.fecha_nacimiento.isoformat() if paciente.fecha_nacimiento else None,
        "edad": paciente.edad,
        "sexo": paciente.sexo,
        "telefono": paciente.telefono,
        "tipo_sangre": paciente.tipo_sangre,
        "alergias": paciente.alergias,
        "condiciones_cronicas": paciente.condiciones_cronicas
    }
    
    # Buscar datos de última consulta (peso, altura, sector) - OPTIMIZADO
    from saas.consultas.models import Consulta
    ultima_consulta = Consulta.query.with_entities(
        Consulta.peso,
        Consulta.altura,
        Consulta.sector,
        Consulta.fecha_hora,
        Consulta.turno
    ).filter_by(
        paciente_id=paciente.id
    ).order_by(Consulta.fecha_hora.desc()).first()
    
    if ultima_consulta:
        data["ultima_consulta"] = {
            "peso": ultima_consulta.peso,
            "altura": ultima_consulta.altura,
            "sector": ultima_consulta.sector,
            "fecha": ultima_consulta.fecha_hora.strftime("%d/%m/%Y"),
            "turno": ultima_consulta.turno
        }
    
    return jsonify({
        "ok": True, 
        "found": True, 
        "paciente": data
    }), 200


# ============================================================================
# RUTAS CRUD - PACIENTES
# ============================================================================

@main_bp.route('/pacientes/nuevo', methods=['GET', 'POST'])
@login_required
def paciente_nuevo():
    """Crear nuevo paciente"""
    # Formulario estándar
    form = PacienteForm()
    
    # Cargar médicos para el select
    medicos = Usuario.query.filter_by(rol='medico', activo=True).all()
    form.medico_id.choices = [(0, 'Sin asignar')] + [(m.id, m.nombre_completo) for m in medicos]
    
    if form.validate_on_submit():
        paciente = Paciente(
            cedula=form.cedula.data,
            nombre=form.nombre.data,
            apellido=form.apellido.data,
            fecha_nacimiento=form.fecha_nacimiento.data,
            sexo=form.sexo.data,
            telefono=form.telefono.data,
            email=form.email.data,
            direccion=form.direccion.data,
            ciudad=form.ciudad.data,
            estado=form.estado.data,
            tipo_sangre=form.tipo_sangre.data,
            alergias=form.alergias.data,
            condiciones_cronicas=form.condiciones_cronicas.data,
            contacto_emergencia_nombre=form.contacto_emergencia_nombre.data,
            contacto_emergencia_telefono=form.contacto_emergencia_telefono.data,
            contacto_emergencia_relacion=form.contacto_emergencia_relacion.data,
            medico_id=form.medico_id.data if form.medico_id.data != 0 else None
        )
        
        db.session.add(paciente)
        db.session.commit()
        
        flash(f'Paciente {paciente.nombre_completo} creado exitosamente.', 'success')
        return redirect(url_for('main.paciente_detalle', id=paciente.id))
    
    return render_template('main/paciente_form.html', form=form, titulo='Nuevo Paciente')


@main_bp.route('/pacientes/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def paciente_editar(id):
    """Editar paciente existente"""
    paciente = Paciente.query.get_or_404(id)
    
    # Verificar permisos
    if current_user.es_medico and not current_user.es_admin:
        if paciente.medico_id != current_user.id:
            flash('No tienes permisos para editar este paciente.', 'danger')
            return redirect(url_for('main.pacientes'))
    
    form = PacienteForm(paciente_id=paciente.id, obj=paciente)
    
    # Cargar médicos para el select
    medicos = Usuario.query.filter_by(rol='medico', activo=True).all()
    form.medico_id.choices = [(0, 'Sin asignar')] + [(m.id, m.nombre_completo) for m in medicos]
    
    if form.validate_on_submit():
        paciente.cedula = form.cedula.data
        paciente.nombre = form.nombre.data
        paciente.apellido = form.apellido.data
        paciente.fecha_nacimiento = form.fecha_nacimiento.data
        paciente.sexo = form.sexo.data
        paciente.telefono = form.telefono.data
        paciente.email = form.email.data
        paciente.direccion = form.direccion.data
        paciente.ciudad = form.ciudad.data
        paciente.estado = form.estado.data
        paciente.tipo_sangre = form.tipo_sangre.data
        paciente.alergias = form.alergias.data
        paciente.condiciones_cronicas = form.condiciones_cronicas.data
        paciente.contacto_emergencia_nombre = form.contacto_emergencia_nombre.data
        paciente.contacto_emergencia_telefono = form.contacto_emergencia_telefono.data
        paciente.contacto_emergencia_relacion = form.contacto_emergencia_relacion.data
        paciente.medico_id = form.medico_id.data if form.medico_id.data != 0 else None
        
        db.session.commit()
        
        flash(f'Paciente {paciente.nombre_completo} actualizado exitosamente.', 'success')
        return redirect(url_for('main.paciente_detalle', id=paciente.id))
    
    # Pre-seleccionar médico actual
    if not form.is_submitted():
        form.medico_id.data = paciente.medico_id if paciente.medico_id else 0
    
    return render_template('main/paciente_form.html', form=form, titulo='Editar Paciente', paciente=paciente)


@main_bp.route('/pacientes/<int:id>/eliminar', methods=['POST'])
@login_required
def paciente_eliminar(id):
    """Eliminar (desactivar) paciente"""
    paciente = Paciente.query.get_or_404(id)
    
    # Solo admin puede eliminar
    if not current_user.es_admin:
        flash('No tienes permisos para eliminar pacientes.', 'danger')
        return redirect(url_for('main.pacientes'))
    
    paciente.activo = False
    db.session.commit()
    
    flash(f'Paciente {paciente.nombre_completo} desactivado exitosamente.', 'success')
    return redirect(url_for('main.pacientes'))


# ============================================================================
# RUTAS CRUD - CITAS
# ============================================================================

@main_bp.route('/citas/nueva', methods=['GET', 'POST'])
@login_required
def cita_nueva():
    """Crear nueva cita"""
    form = CitaForm()
    
    # Cargar pacientes y médicos para los selects
    pacientes = Paciente.query.filter_by(activo=True).order_by(Paciente.nombre).all()
    form.paciente_id.choices = [(p.id, p.nombre_completo) for p in pacientes]
    
    medicos = Usuario.query.filter_by(rol='medico', activo=True).order_by(Usuario.nombre).all()
    form.medico_id.choices = [(m.id, m.nombre_completo) for m in medicos]
    
    # Si es médico, pre-seleccionar su ID
    if current_user.es_medico and not form.is_submitted():
        form.medico_id.data = current_user.id
    
    if form.validate_on_submit():
        cita = Cita(
            paciente_id=form.paciente_id.data,
            medico_id=form.medico_id.data,
            fecha_hora=form.fecha_hora.data,
            duracion_minutos=form.duracion_minutos.data,
            motivo=form.motivo.data,
            tipo_cita=form.tipo_cita.data,
            estado=form.estado.data,
            observaciones=form.observaciones.data
        )
        
        db.session.add(cita)
        db.session.commit()
        
        flash('Cita creada exitosamente.', 'success')
        return redirect(url_for('main.citas'))
    
    return render_template('main/cita_form.html', form=form, titulo='Nueva Cita')


@main_bp.route('/citas/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def cita_editar(id):
    """Editar cita existente"""
    cita = Cita.query.get_or_404(id)
    
    # Verificar permisos
    if current_user.es_medico and not current_user.es_admin:
        if cita.medico_id != current_user.id:
            flash('No tienes permisos para editar esta cita.', 'danger')
            return redirect(url_for('main.citas'))
    
    form = CitaForm(obj=cita)
    
    # Cargar pacientes y médicos para los selects
    pacientes = Paciente.query.filter_by(activo=True).order_by(Paciente.nombre).all()
    form.paciente_id.choices = [(p.id, p.nombre_completo) for p in pacientes]
    
    medicos = Usuario.query.filter_by(rol='medico', activo=True).order_by(Usuario.nombre).all()
    form.medico_id.choices = [(m.id, m.nombre_completo) for m in medicos]
    
    if form.validate_on_submit():
        cita.paciente_id = form.paciente_id.data
        cita.medico_id = form.medico_id.data
        cita.fecha_hora = form.fecha_hora.data
        cita.duracion_minutos = form.duracion_minutos.data
        cita.motivo = form.motivo.data
        cita.tipo_cita = form.tipo_cita.data
        cita.estado = form.estado.data
        cita.observaciones = form.observaciones.data
        
        db.session.commit()
        
        flash('Cita actualizada exitosamente.', 'success')
        return redirect(url_for('main.citas'))
    
    return render_template('main/cita_form.html', form=form, titulo='Editar Cita', cita=cita)


@main_bp.route('/citas/<int:id>/cancelar', methods=['POST'])
@login_required
def cita_cancelar(id):
    """Cancelar cita"""
    cita = Cita.query.get_or_404(id)
    
    # Verificar permisos
    if current_user.es_medico and not current_user.es_admin:
        if cita.medico_id != current_user.id:
            flash('No tienes permisos para cancelar esta cita.', 'danger')
            return redirect(url_for('main.citas'))
    
    cita.estado = 'cancelada'
    db.session.commit()
    
    flash('Cita cancelada exitosamente.', 'success')
    return redirect(url_for('main.citas'))
