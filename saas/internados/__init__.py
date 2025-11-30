from flask import Blueprint

bp = Blueprint('internados', __name__)

from . import routes
