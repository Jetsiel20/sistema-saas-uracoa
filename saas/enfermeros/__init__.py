from flask import Blueprint
enfermeros_bp = Blueprint('enfermeros', __name__)
from . import routes
