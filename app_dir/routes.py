from datetime import datetime
from guess_language import guess_language
from flask import render_template, flash, redirect, url_for, request, g, jsonify
from app_dir import app, db
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app_dir.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm, \
                            ResetPasswordForm, ResetPasswordRequestForm
from app_dir.models import User, Post
from app_dir.email import send_password_reset_email
from app_dir.translate import translate


@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    # g.locale == zh， zh-CN 或者 zh-TW之类的
    g.locale = request.accept_languages[0][0]


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        language = guess_language(form.post.data)
        if language == 'UNKNOWN' or len(language) > 5:
            language = ''
        post = Post(body=form.post.data, author=current_user, language=language)
        db.session.add(post)
        db.session.commit()
        flash('Your post is now live!')
        return redirect(url_for('index'))
    page = request.args.get('page', 1, type=int)
    pagination = current_user.stars_posts().paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    posts = pagination.items
    next_url = url_for('index', page=pagination.next_num) \
        if pagination.has_next else None
    prev_url = url_for('index', page=pagination.prev_num) \
        if pagination.has_prev else None
    return render_template('index.html', title='Home Page', form=form, posts=posts,
                           next_url=next_url, prev_url=prev_url)


@app.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    posts = pagination.items
    next_url = url_for('explore', page=pagination.next_num) \
        if pagination.has_next else None
    prev_url = url_for('explore', page=pagination.prev_num) \
        if pagination.has_prev else None
    return render_template('index.html', title='Explore', posts=posts,
                           next_url=next_url, prev_url=prev_url)


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
            flash('Invalid username or password.')
            return redirect(url_for('login'))
        login_user(user=user, remember=form.remember_me.data)
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
        flash('Congratulations you are now a registered user. You can log in now!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    posts = pagination.items
    next_url = url_for('user', username=user.username, page=pagination.next_num) \
        if pagination.has_next else None
    prev_url = url_for('user', username=user.username, page=pagination.prev_num) \
        if pagination.has_prev else None
    return render_template('user.html', user=user, posts=posts,
                           next_url=next_url, prev_url=prev_url)


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


@app.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
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


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
            flash('Check your email for the instructions to reset your password.')
            return redirect(url_for('login'))
        else:
            flash('This email haven\'t registered.')
            return redirect(url_for('reset_password_request'))
    return render_template('reset_password_request.html',
                           title='Reset Password', form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    user = User.verify_reset_password_token(token)
    if not user:
        flash('Invalid token!')
        return redirect(url_for('index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash('Your password has been reset.')
        return redirect(url_for('login'))
    return render_template('reset_password.html', form=form)


@app.route('/translate', methods=['post'])
@login_required
def translate_text():
    return jsonify({'text': translate(request.form['text'],
                                      request.form['source_language'],
                                      request.form['target_language'])})


@app.route('/test')
def test():
    # for testing only
    return ''
