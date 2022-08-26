import datetime as dt
import os

from flask import Flask, render_template, abort, flash, redirect, url_for, Response
from flask_bootstrap import Bootstrap4
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from forms import RegisterForm, LoginForm
from functools import wraps
import mealbrain

# app config
app = Flask(__name__)
Bootstrap4(app)
app.config['SECRET_KEY'] = 'PLACEHOLDER'
app.config['BOOTSTRAP_BTN_STYLE'] = 'success'
login_manager = LoginManager()
login_manager.init_app(app)

# connect to database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///blog.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# database tables config
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), nullable=False, unique=True)
    password = db.Column(db.String(250), nullable=False)
    name = db.Column(db.String(250), nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)

    def __init__(self, email, password, name, confirmed, admin=False, confirmed_on=None):
        self.email = email
        self.password = password
        self.name = name
        self.admin = admin
        self.registered_on = dt.datetime.now()
        self.confirmed = confirmed
        self.registered_on = confirmed_on


db.create_all()


def admin_required(f):
    @wraps(f)
    def decorated_f(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_f


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=int(user_id)).first()


@app.route("/")
def home() -> str:
    """Takes the login status.
    Renders the homepage.
    Homepage looks differently, depending on the login status:
    - logged in: calendar view for the current user and search
    - logged out: search/call to action"""
    return render_template('/home.html')


@app.route('/register', methods=['GET', 'POST'])
def register() -> str or Response:
    """Renders the register page.
    If email already exits, redirects to login page.
    If input data is invalid, redirects to register w/ flash."""
    form = RegisterForm()
    if form.validate_on_submit():
        check_email = User.query.filter_by(email=form.email.data).first()
        if check_email:
            flash('This email has already been registered.')
            return redirect(url_for('login'))
        if form.password.data != form.confirmation.data:
            flash('Password and confirmation do not match, please try again.')
            return redirect(url_for('register'))
        if len(form.password.data) < 8:
            flash('Please make sure password is at least 8 characters long.')
            return redirect(url_for('register'))
        new_user = User(
            email=form.email.data,
            password=generate_password_hash(form.password.data),
            name=form.name.data,
            confirmed=False
        )
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('home'))
    return render_template('register.html', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login() -> str or Response:
    """Renders the login page.
    If input data is invalid, redirects to register/login page.
    If input data is valid, redirects to homepage.
    """
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None:
            flash('You need to register in order to log in.')
            return redirect(url_for('register'))
        elif not check_password_hash(user.password, form.password.data):
            flash('Wrong password or email, try again.')
            return redirect(url_for('login'))
        else:
            flash('Login successful.')
            login_user(user)
            return redirect(url_for('home'))
    return render_template('/login.html')


@app.route('/logout')
@login_required
def logout() -> Response:
    logout_user()
    return redirect(url_for('home'))


@app.route("/search/<user_input>")
def search(user_input):
    """Takes the user input.
    Renders the result of search:
    - found meal/product that has the most fitting name
    - found table of replacements for that meal (sortable)
    - if meal not found: prompt to add"""
    return f"Searches the replacement for '{user_input}'"


@app.route("/contact")
def contact():
    """Returns simple contact page."""
    return "Contact info"


@app.route("/settings")
def settings():
    """Takes user's ID.
    Returns customizable user settings:
    - language
    - diet
    - password change (*)"""
    return "Settings"


@app.route("/day/<date>")
def day(date):
    """Takes user's ID and date.
    Renders customizable diet for the current date."""
    return f"Diet for {date}"


if __name__ == "__main__":
    app.run(debug=True)
