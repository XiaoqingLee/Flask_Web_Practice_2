from flask import Flask

app = Flask(__name__)

from app_dir import routes

