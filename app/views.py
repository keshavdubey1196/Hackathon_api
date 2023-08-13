from app import app


@app.route('/home', methods=['GET'])
def info():
    return "<h1>This is home route</h1>"
