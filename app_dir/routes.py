from app_dir import app

@app.route('/')
@app.route('/index')
def index():
    user = {'username': "Xiaoqing"}
    html = """
    <html>
        <head>
            <title>Home Page - Microblog</title>
        </head>
        <body>
            <h1>Hello, {} !<h1>
        </body>
    </html>
        """
    return html.format(user['username'])

