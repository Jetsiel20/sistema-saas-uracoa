from flask import Blueprint
laboratorio_bp = Blueprint('laboratorio', __name__)
from . import routes
