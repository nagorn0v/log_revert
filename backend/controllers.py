from app import app


@app.route('/')
def hello_world():
    return "<p>Hello from flask</p>"


@app.route('/test')
def test():
    return '<h1>test message</h1>'