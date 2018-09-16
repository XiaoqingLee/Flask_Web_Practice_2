import os


# 静态类，不必实例化
class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'who-will-know-what-am-i'

