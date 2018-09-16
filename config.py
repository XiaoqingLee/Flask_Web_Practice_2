import os
basedir = os.path.abspath(os.path.dirname(__file__))

# 静态类，不必实例化
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'who-will-know-what-am-i'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False


