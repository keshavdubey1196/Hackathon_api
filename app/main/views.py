from flask import Blueprint


main = Blueprint('main', __name__)


@main.route('/info', methods=['GET'])
def info():
    return "<h1>This is home route</h1>"
