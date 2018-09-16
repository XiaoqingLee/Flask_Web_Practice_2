from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
login = LoginManager(app)
# 当匿名用户请求访问login_required修饰的端点时，在login_required修饰过的的
# 函数内部，自动将用户重定向到login.login_view端点，同时在新请求的url后面
# 添加？next=<url_for(原始请求的端点名用)>
login.login_view = 'login'


from app_dir import routes, models

