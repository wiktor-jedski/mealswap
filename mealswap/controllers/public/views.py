from flask import render_template, Blueprint, redirect, url_for, Response
from flask_login import current_user

blueprint = Blueprint('public', __name__, static_folder='../static')


@blueprint.route("/")
def home() -> str or Response:
    """Renders the homepage.

    Homepage looks differently, depending on the login status:
    - logged in: calendar view for the current user and search
    - logged out: call to action

    :return: rendered home template OR
        redirect to calendar if logged in
    """
    if current_user.is_active:
        return redirect(url_for('diet.calendar'))
    else:
        return render_template('public/home.html', user=current_user)


@blueprint.route("/contact")
def contact() -> str:
    """Renders contact info.

    :return: rendered contact template
    """
    return render_template('public/contact.html', user=current_user)


@blueprint.route("/license")
def license_info() -> str:
    """Renders license info

    :return: rendered license template
    """
    return render_template('public/license.html', user=current_user)


@blueprint.route('/tos')
def tos() -> str:
    """Renders terms of service info

    :return: rendered TOS template
    """
    return render_template('public/tos.html', user=current_user)
