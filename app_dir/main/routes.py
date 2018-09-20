from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g, jsonify, current_app
from flask_login import current_user, login_required
from guess_language import guess_language
from app_dir import db
from app_dir.models import User, Post
from app_dir.translate import translate
from app_dir.main import bp
from app_dir.main.forms import EditProfileForm, PostForm


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    # g.locale == zh， zh-CN 或者 zh-TW之类的
    # 从接受一个请求到返回一个请求，我们从头到尾在同一个线程中访问的g
    g.locale = request.accept_languages[0][0]


@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
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
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    pagination = current_user.stars_posts().paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    posts = pagination.items
    next_url = url_for('main.index', page=pagination.next_num) \
        if pagination.has_next else None
    prev_url = url_for('main.index', page=pagination.prev_num) \
        if pagination.has_prev else None
    return render_template('index.html', title='Home Page', form=form, posts=posts,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    posts = pagination.items
    next_url = url_for('main.explore', page=pagination.next_num) \
        if pagination.has_next else None
    prev_url = url_for('main.explore', page=pagination.prev_num) \
        if pagination.has_prev else None
    return render_template('index.html', title='Explore', posts=posts,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    pagination = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    posts = pagination.items
    next_url = url_for('main.user', username=user.username, page=pagination.next_num) \
        if pagination.has_next else None
    prev_url = url_for('main.user', username=user.username, page=pagination.prev_num) \
        if pagination.has_prev else None
    return render_template('user.html', user=user, posts=posts,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('Your changes have been saved.')
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='Edit Profile', form=form)


@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You can not follow yourself!')
        return redirect(url_for('main.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}.'.format(username))
    return redirect(url_for('main.user', username=username))


@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('User {} not found.'.format(username))
        return redirect(url_for('main.index'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(username))
    return redirect(url_for('main.user', username=username))


@bp.route('/translate', methods=['post'])
@login_required
def translate_text():
    return jsonify({'text': translate(request.form['text'],
                                      request.form['source_language'],
                                      request.form['target_language'])})

