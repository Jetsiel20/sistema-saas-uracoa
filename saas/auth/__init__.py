"""
Blueprint de Autenticación
Hospital Tipo 1 Uracoa - J&S Software Inteligentes
"""
from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

from saas.auth import routes
