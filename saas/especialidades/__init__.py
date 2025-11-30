from flask import Blueprint
especialidades_bp = Blueprint('especialidades', __name__)
from . import routes
