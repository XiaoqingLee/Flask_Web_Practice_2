from flask import Blueprint


bp = Blueprint('errors', __name__)


from app_dir.errors import handlers

