from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'who-will-know-what-am-i'

from app_dir import routes

