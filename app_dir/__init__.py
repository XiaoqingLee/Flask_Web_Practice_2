import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
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


if not app.debug:
    if app.config['MAIL_SERVER']:
        auth = None
        if app.config['MAIL_USERNAME']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure =()
        mail_handler = SMTPHandler(
            mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr=auth[0],
            toaddrs=app.config['ADMINS'],
            subject='Microblog Failure',
            credentials=auth,
            secure=secure
        )
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


from app_dir import routes, models, errors

