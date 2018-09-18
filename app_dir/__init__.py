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
    # 邮件错误输出
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
        mail_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [ in %(pathname)s:%(lineno)d ]'
        ))
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)
    # 本地日志错误输出
    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/microblog.log',
                                       maxBytes=1024000,
                                       backupCount=50
                                       )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [ in %(pathname)s:%(lineno)d ]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    # 针对应用本身
    app.logger.setLevel(logging.INFO)
    app.logger.info('Microblog starup')


from app_dir import routes, models, errors

