from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from app_dir import app, db
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app_dir.forms import LoginForm, RegistrationForm, EditProfileForm
from app_dir.models import User


@app.route('/')
@app.route('/index')
@login_required
def index():
    posts = [
        {
            'author': {'username': 'John'},
            'body': 'Beautiful day in Porland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movies was so cool!'
        }
    ]
    return render_template('index.html', title='Home Page', posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()  # 这是一个登录表单
    # [1]form.validate_on_submit() 仅仅对submit按钮按下发送post请求时候的数据做验证
    # form.validate() 对上述post情景和首次get方式访问表单页面的两个情景发送的数据都
    # 验证，所以如果携程这个函数，那么首次访问login时候，form.<field>.errors不为空
    # [2]个人认为，用户填写表单post到这里之后，form = LoginForm()会将post的信息“丰富”form对象，
    # 在validate_on_submit()函数中，表单对象会验证Field的validator参数（用html属性无法完成的那些）和
    # 若干个我们自己定义的格式符合validate_<field_variable>(<field_variable>)的验证函数。
    # 通过格式验证后返回True。
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user=user, remember=form.remember_me.data)
        flash('Login succeed for user {}, remember_me={}.'.format(
            form.username.data, form.remember_me.data))
        # request.args是一个字典，用get访问比较安全
        next_page = request.args.get('next') # next_page的值是路径，不是端点名
        # 没有next参数或者next参数值是个有着完整协议和域名的非本地相对路径请求（如http://www.baidu.com）
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data, email=form.email.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Congratulations you are now a registered user. You can login now!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    posts = [
        {'author': user, 'body': 'Test post #1'},
        {'author': user, 'body': 'Test post #2'}
    ]
    return render_template('user.html', user=user, posts=posts)


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)



@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@app.route('/follow/<username>')
@login_required()
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You can not follow yourself!')
        return redirect(url_for('user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}.'.format(username))
    return redirect(url_for('user', username=username))


@app.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('user', username=username))




