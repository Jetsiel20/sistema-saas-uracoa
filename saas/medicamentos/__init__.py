"""
Módulo de Medicamentos - Inventario Institucional
Sistema adaptado para hospital público rural
Sin funciones de venta, solo control de disponibilidad
"""
from flask import Blueprint

medicamentos_bp = Blueprint('medicamentos', __name__, url_prefix='/medicamentos')

from saas.medicamentos import routes
