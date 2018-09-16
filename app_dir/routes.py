from app_dir import app

@app.route('/')
@app.route('/index')
def index():
    return "Hello world!"
