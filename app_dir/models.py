from hashlib import md5
from datetime import datetime
from app_dir import db, login
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


# 关系表，实现User到User的多对多关系
# A fan follows a star. The left User follows the right User.
# 这个关系表我们不会直接操作， 而是通过user_object.stars 和 user_object.fans 进行简介管理
following_relationship_table = db.Table(
    'follows',
    db.Column('fan_id', db.Integer, db.ForeignKey('user.id')),  # User 对象的表名是小写的user
    db.Column('star_id', db.Integer, db.ForeignKey('user.id'))
)


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
    about_me = db.Column(db.String(140))
    last_seen = db.Column(db.DateTime, default=datetime.utcnow)
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    # 左侧对象通过 self.stars 找到关联的右侧对象
    stars = db.relationship(
        'User',  # Left is self, right is User
        secondary=following_relationship_table,  # according to what
        primaryjoin=(following_relationship_table.c.fan_id == id),   # 关系表左侧的对象和user表的join
        secondaryjoin=(following_relationship_table.c.star_id == id),  # 关系表右侧的对象和user表的join
        backref=db.backref('fans',  # 右侧对象通过.fans找到关联的左侧对象
                           lazy='dynamic'),
        lazy='dynamic'
    )

    def __repr__(self):
        return '<User {}>'.format(self.username)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return 'https://www.gravatar.com/avatar/{}?d=identicon&s={}'.format(digest, size)

    def follow(self, user):
        if not self.is_following(user):
            self.stars.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.stars.remove(user)

    def is_following(self, user):
        return self.stars.filter(following_relationship_table.c.star_id == user.id).count() > 0

    def stars_posts(self):
        # post 表和 following_relationship_table 联结
        stars_posts = Post.query.join(
            following_relationship_table,
            (following_relationship_table.c.star_id == Post.user_id)
        ).filter(following_relationship_table.c.fan_id == self.id)
        own_posts = Post.query.filter_by(user_id=self.id)
        return stars_posts.union(own_posts).order_by(Post.timestamp.desc())


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



