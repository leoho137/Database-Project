import os

from flask import Flask
from flask_mysqldb import MySQL
from flask_login import LoginManager
def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
    )
    app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = 'root'
    app.config['MYSQL_PASSWORD'] = 'root'
    app.config['MYSQL_DB'] = 'DatabaseProject'
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    import db
    db.init_app(app)
    from auth import create_auth_blueprint
    from item import bp as item_bp
    from order import bp as order_bp
    from donation import bp as donation_bp
    auth_bp = create_auth_blueprint(login_manager)
    app.register_blueprint(auth_bp)
    app.register_blueprint(item_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(donation_bp)
    app.add_url_rule('/', endpoint='auth.login')

    #  a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    return app

if __name__ == "__main__":
    app = create_app()
    app.run('127.0.0.1', 5000, debug = True)