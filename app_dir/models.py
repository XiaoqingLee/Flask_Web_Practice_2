from app_dir import db, login
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


# 继承UserMixin之后， User就有了一下四个属性（或方法），这四项Flask_Login工作的时候需要使用
# is_authenticated: 一个用来表示用户是否通过登录认证的属性，用True和False表示。
# is_active: 如果用户账户是活跃的，那么这个属性是True，否则就是False（译者注：活跃用户的定义是该用户的登录状态是否通过用户名密码登录，通过“记住我”功能保持登录状态的用户是非活跃的）。
# is_anonymous: 常规用户的该属性是False，对特定的匿名用户是True。
# get_id(): 返回用户的唯一id的方法，返回值类型是字符串(Python2 下返回unicode字符串).

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    posts = db.relationship('Post', backref='author', lazy='dynamic')

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Flask_Login 要求我们自己写一个提供用户id（id是字符串形式）返回用户实例的函数以供他调用, 这个函数用 login对象的user_loader装饰器装饰
@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String(140))
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return '<Post {}>'.format(self.body)



