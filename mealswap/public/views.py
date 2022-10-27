from pathlib import Path

from flask import render_template, Blueprint, redirect, url_for, Response, request
from flask_login import current_user
from mealswap.controller.controls import get_element_by_id, Model
from mealswap.extensions import login_manager

blueprint = Blueprint('public', __name__, static_folder='../static')


@login_manager.user_loader
def load_user(user_id):
    return get_element_by_id(Model.USER, user_id)


@blueprint.route("/")
def home() -> str or Response:
    """Renders the homepage.
    Homepage looks differently, depending on the login status:
    - logged in: calendar view for the current user and search
    - logged out: call to action"""
    if current_user.is_active:
        return redirect(url_for('diet.calendar'))
    else:
        return render_template('public/home.html', user=current_user)


@blueprint.route("/contact")
def contact() -> str:
    """Renders contact info."""
    return render_template('public/contact.html', user=current_user)


@blueprint.route("/license")
def license_info() -> str:
    """Renders license info"""
    return render_template('public/license.html', user=current_user)


@blueprint.route('/tos')
def tos() -> str:
    """Renders terms of service info"""
    return render_template('public/tos.html', user=current_user)
