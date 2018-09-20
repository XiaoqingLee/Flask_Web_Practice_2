from flask import render_template, flash, redirect, url_for, request
from werkzeug.urls import url_parse
from flask_login import current_user, login_user, logout_user
from app_dir import db
from app_dir.auth import bp
from app_dir.auth.forms import LoginForm, RegistrationForm,  \
                               ResetPasswordForm, ResetPasswordRequestForm
from app_dir.auth.email import send_password_reset_email
from app_dir.models import User


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
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
            flash('Invalid username or password.')
            return redirect(url_for('auth.login'))
        login_user(user=user, remember=form.remember_me.data)
        # request.args是一个字典，用get访问比较安全
        next_page = request.args.get('next')  # next_page的值是路径，不是端点名
        # 没有next参数或者next参数值是个有着完整协议和域名的非本地相对路径请求（如http://www.baidu.com）
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='Sign In', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(username=form.username.data, email=form.email.data)
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Congratulations you are now a registered user. You can log in now!')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='Register', form=form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            flash('Check your email for the instructions to reset your password.')
            return redirect(url_for('auth.login'))
        else:
            flash('This email haven\'t registered. Check your input.')
            return redirect(url_for('auth.reset_password_request'))
    return render_template('auth/reset_password_request.html',
                           title='Reset Password', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        flash('Invalid token!')
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)

