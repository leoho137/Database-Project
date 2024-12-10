import mysql.connector
from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, current_app
)
from werkzeug.security import check_password_hash, generate_password_hash
from db import get_db
from flask_login import LoginManager, UserMixin
from flask_login import login_user, logout_user, current_user, login_required
# Define your User class that extends UserMixin
class User(UserMixin):
    def __init__(self, username):
        self.username = username
    def get_id(self):
        # Use username as the unique identifier for Flask-Login
        return self.username
def create_auth_blueprint(login_manager: LoginManager):
    bp = Blueprint('auth', __name__, url_prefix='/auth')

    #login_manager.init_app(current_app)

    @login_manager.user_loader
    def load_user(username):
        db = get_db()
        cursor = db.cursor()
        cursor.execute('SELECT * FROM Person WHERE userName = %s', (username,))
        columns = [column[0] for column in cursor.description]
        res = cursor.fetchone()
        res_dict = dict(zip(columns, res))
        if len(res_dict) == 0:
            return None
        else:
            username = res_dict.get("userName")
            return User(username)



    @bp.route('/register', methods=('GET', 'POST'))
    def register():
        if request.method == 'POST':
            username = request.form['userName']
            password = request.form['password']
            fname = request.form['fname']
            lname = request.form['lname']
            email = request.form['email']
            db = get_db()
            print(db)
            error = None
            cursor = db.cursor()
            cursor.execute("SELECT 1 FROM Person WHERE userName = %s", (username,))
            existing_user = cursor.fetchone()
            if not username:
                error = 'Username is required.'
            elif not password:
                error = 'Password is required.'
            elif (not fname) or (not lname):
                error = 'Name is required.'
            elif not email:
                error = 'Email Address is required.'
            elif existing_user:
                error = f"User {username} is already registered."

            if error is None:
                try:
                    cursor.execute(
                        "INSERT INTO Person (userName, password, fname, lname, email) "
                        "VALUES (%s, %s, %s, %s, %s)",
                        (username, generate_password_hash(password), fname, lname, email),
                    )
                    db.commit()
                except mysql.connector.IntegrityError:
                    error = f"User {username} is already registered."
                else:
                    return redirect(url_for("auth.login"))

            flash(error)

        return render_template('auth/register.html')



    @bp.route('/login', methods=('GET', 'POST'))
    def login():

        if current_user.is_authenticated:
            return redirect(url_for('auth.index'))

        if request.method == 'POST':
            username = request.form['userName']
            password = request.form['password']
            db = get_db()
            cursor = db.cursor()
            error = None
            cursor.execute(
                'SELECT * FROM Person WHERE userName = %s', (username,)
            )
            columns = [column[0] for column in cursor.description]
            print(columns)
            user = cursor.fetchone()
            if user is None:
                error = 'Non-existing username'
            elif not check_password_hash(user[1], password):
                error = 'Incorrect password.'



            if error is None:
                res_dict = dict(zip(columns, user))
                username = res_dict.get("userName")
                wrapped_user=User(username)
                login_user(wrapped_user)
                return redirect(url_for('auth.index'))  # change to your main page here
            flash(error)

        return render_template('auth/login.html')

    @bp.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('auth.login'))

    @bp.route('/index', methods=('GET', 'POST'))
    def index():
        return render_template('auth/index.html')

    return bp


