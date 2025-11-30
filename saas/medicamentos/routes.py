"""
Rutas del módulo Medicamentos
Inventario institucional para hospital público rural
"""
from datetime import datetime, date
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from saas.medicamentos import medicamentos_bp
from saas.medicamentos.forms import MedicamentoForm
from saas.models import Medicamento
from saas.extensions import db


@medicamentos_bp.route('/')
@login_required
def index():
    """Lista de medicamentos con filtros y badges de estado"""
    page = request.args.get('page', 1, type=int)
    filtro = request.args.get('filtro', 'todos')
    buscar = request.args.get('buscar', '').strip()
    
    query = Medicamento.query.filter_by(activo=True)
    
    # Aplicar búsqueda
    if buscar:
        query = query.filter(
            db.or_(
                Medicamento.nombre.ilike(f'%{buscar}%'),
                Medicamento.nombre_generico.ilike(f'%{buscar}%')
            )
        )
    
    # Aplicar filtros
    if filtro == 'bajo_stock':
        query = query.filter(Medicamento.cantidad_stock <= Medicamento.stock_minimo)
    elif filtro == 'vencido':
        query = query.filter(Medicamento.fecha_vencimiento < date.today())
    elif filtro == 'por_vencer':
        # Medicamentos que vencen en los próximos 30 días
        from datetime import timedelta
        fecha_limite = date.today() + timedelta(days=30)
        query = query.filter(
            Medicamento.fecha_vencimiento.between(date.today(), fecha_limite)
        )
    
    medicamentos = query.order_by(Medicamento.nombre).paginate(
        page=page, per_page=20, error_out=False
    )
    
    # Contadores para badges
    total = Medicamento.query.filter_by(activo=True).count()
    bajo_stock = Medicamento.query.filter(
        Medicamento.activo == True,
        Medicamento.cantidad_stock <= Medicamento.stock_minimo
    ).count()
    vencidos = Medicamento.query.filter(
        Medicamento.activo == True,
        Medicamento.fecha_vencimiento < date.today()
    ).count()
    
    return render_template(
        'medicamentos/index.html',
        medicamentos=medicamentos,
        filtro=filtro,
        buscar=buscar,
        total=total,
        bajo_stock=bajo_stock,
        vencidos=vencidos
    )


@medicamentos_bp.route('/nuevo', methods=['GET', 'POST'])
@login_required
def crear():
    """Crear nuevo medicamento en inventario"""
    form = MedicamentoForm()
    
    if form.validate_on_submit():
        medicamento = Medicamento(
            nombre=form.nombre.data,
            nombre_generico=form.nombre_generico.data,
            presentacion=form.presentacion.data,
            concentracion=form.concentracion.data,
            codigo_barras=form.codigo_barras.data if form.codigo_barras.data else None,
            registro_sanitario=form.registro_sanitario.data,
            laboratorio=form.laboratorio.data,
            cantidad_stock=form.cantidad_stock.data,
            unidad_medida=form.unidad_medida.data,
            stock_minimo=form.stock_minimo.data,
            fecha_vencimiento=form.fecha_vencimiento.data,
            requiere_receta=bool(form.requiere_receta.data),
            observaciones=form.observaciones.data,
            responsable_id=current_user.id
        )
        
        db.session.add(medicamento)
        db.session.commit()
        
        flash(f'Medicamento "{medicamento.nombre}" agregado al inventario', 'success')
        return redirect(url_for('medicamentos.index'))
    
    return render_template('medicamentos/form.html', form=form, title='Nuevo Medicamento')


@medicamentos_bp.route('/<int:id>')
@login_required
def detalle(id):
    """Ver detalle de medicamento"""
    medicamento = Medicamento.query.get_or_404(id)
    return render_template('medicamentos/detalle.html', medicamento=medicamento)


@medicamentos_bp.route('/<int:id>/editar', methods=['GET', 'POST'])
@login_required
def editar(id):
    """Editar medicamento"""
    medicamento = Medicamento.query.get_or_404(id)
    form = MedicamentoForm(obj=medicamento)
    
    if form.validate_on_submit():
        medicamento.nombre = form.nombre.data
        medicamento.nombre_generico = form.nombre_generico.data
        medicamento.presentacion = form.presentacion.data
        medicamento.concentracion = form.concentracion.data
        medicamento.codigo_barras = form.codigo_barras.data if form.codigo_barras.data else None
        medicamento.registro_sanitario = form.registro_sanitario.data
        medicamento.laboratorio = form.laboratorio.data
        medicamento.cantidad_stock = form.cantidad_stock.data
        medicamento.unidad_medida = form.unidad_medida.data
        medicamento.stock_minimo = form.stock_minimo.data
        medicamento.fecha_vencimiento = form.fecha_vencimiento.data
        medicamento.requiere_receta = bool(form.requiere_receta.data)
        medicamento.observaciones = form.observaciones.data
        
        db.session.commit()
        flash(f'Medicamento "{medicamento.nombre}" actualizado', 'success')
        return redirect(url_for('medicamentos.detalle', id=medicamento.id))
    
    return render_template('medicamentos/form.html', form=form, medicamento=medicamento, title='Editar Medicamento')


@medicamentos_bp.route('/<int:id>/eliminar', methods=['POST'])
@login_required
def eliminar(id):
    """Desactivar medicamento (borrado lógico)"""
    medicamento = Medicamento.query.get_or_404(id)
    medicamento.activo = False
    db.session.commit()
    
    flash(f'Medicamento "{medicamento.nombre}" desactivado', 'info')
    return redirect(url_for('medicamentos.index'))
