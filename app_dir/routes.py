from flask import render_template, flash, redirect
from app_dir import app
from app_dir.forms import LoginForm


@app.route('/')
@app.route('/index')
def index():
    user = {'username': "Xiaoqing"}
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
    return render_template('index.html', title='Home', user=user, posts=posts)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    # form.validate_on_submit() 仅仅对submit按钮按下发送post请求时候的数据做验证
    # form.validate() 对上述post情景和首次get方式访问表单页面的两个情景发送的数据都
    # 验证，所以如果携程这个函数，那么首次访问login时候，form.<field>.errors不为空
    if form.validate_on_submit():
        flash('Login requested for user {}, remember_me={}'.format(
            form.username.data, form.remember_me.data))
        return redirect('/index')
    return render_template('login.html', title='Sign In', form=form)


