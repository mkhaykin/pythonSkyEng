from flask import Blueprint, current_app, render_template

main = Blueprint('main', __name__)


@main.route('/favicon.ico')
def favicon():
    return current_app.send_static_file('favicon.ico')


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/about', methods=['GET'])
def about():
    """ about page """
    # TODO:
    return render_template('about.html', title='About')
