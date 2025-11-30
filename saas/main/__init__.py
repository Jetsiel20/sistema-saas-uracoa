"""
Blueprint Principal
Hospital Tipo 1 Uracoa - J&S Software Inteligentes
"""
from flask import Blueprint

main_bp = Blueprint('main', __name__)

from saas.main import routes
