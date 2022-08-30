from flask import render_template, abort, flash, redirect, url_for, Response, Blueprint

from mealswap.extensions import login_manager
from mealswap.user.models import User

blueprint = Blueprint('public', __name__, static_folder='../static')


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=int(user_id)).first()


@blueprint.route("/")
def home() -> str:
    """Takes the login status.
    Renders the homepage.
    Homepage looks differently, depending on the login status:
    - logged in: calendar view for the current user and search
    - logged out: call to action"""
    return render_template('public/home.html')



