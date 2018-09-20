import os
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_mail import Mail
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from config import Config


db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
# 当匿名用户请求访问login_required修饰的端点时，在login_required修饰过的的
# 函数内部，自动将用户重定向到login.login_view端点，同时在新请求的url后面
# 添加？next=<url_for(原始请求的端点名称)>
login.login_view = 'auth.login'
login.login_message = 'Please log in to access this page.'
mail = Mail()
bootstrap = Bootstrap()
moment = Moment()


def create_app(config_class=Config):
    app = Flask(__name__)
    # Config不必实例化
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)
    moment.init_app(app)

    # 在404 和 500页面定义url_prefix意义不大，用户看到这些页面的情况
    # 都是flask重定向的，而且重定向后，地址栏不会更新显示url_prefix.
    from app_dir.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    from app_dir.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')

    # 不要在主页'/',相关的蓝本上定义url_prefix，这样用户访问主页不方便。
    from app_dir.main import bp as main_bp
    app.register_blueprint(main_bp)

    if not app.debug and not app.testing:
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

    return app


from app_dir import models

