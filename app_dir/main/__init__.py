from flask import Blueprint


bp = Blueprint('main', __name__)


from app_dir.main import routes

