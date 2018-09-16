from flask import render_template
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


@app.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html', title='Sign In', form=form)


