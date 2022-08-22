import os

from flask import Flask, render_template, abort
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
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
login_manager = LoginManager()
login_manager.init_app(app)

# connect to database
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///blog.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# database tables config
class User(UserMixin, db.Model):
    __tablename__ = 'app_users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), nullable=False, unique=True)
    password = db.Column(db.String(250), nullable=False)
    name = db.Column(db.String(250), nullable=False)


db.create_all()


def admin_required(f):
    @wraps(f)
    def decorated_f(*args, **kwargs):
        if current_user.id != 1:
            return abort(403)
        return f(*args, **kwargs)
    return decorated_f


@app.route("/")
def homepage():
    """Takes the login status.
    Renders the homepage.
    Homepage looks differently, depending on the login status:
    - logged in: calendar view for the current user and search
    - logged out: search/call to action"""
    return render_template('/home.html')


@app.route("/login")
def login():
    """Takes the login status.
    Renders the homepage.
    Homepage looks differently, depending on the login status:
    - logged in: calendar view for the current user and search
    - logged out: search/call to action"""
    return render_template('/home.html')


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
