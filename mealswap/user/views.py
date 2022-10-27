from flask import render_template, flash, redirect, url_for, Response, Blueprint, abort
from flask_login import login_user, login_required, logout_user, current_user
from mealswap.extensions import login_manager, db
from mealswap.email import send_confirmation_msg
from .forms import RegisterForm, LoginForm
from .token import confirm_token, SignatureExpired, BadSignature
import datetime as dt
from ..controller.controls import add_user, get_user_by_email, get_element_by_id, Model

blueprint = Blueprint('user', __name__, static_folder='../static')


@login_manager.user_loader
def load_user(user_id):
    return get_element_by_id(Model.USER, user_id)


@blueprint.route('/register', methods=['GET', 'POST'])
def register() -> str or Response:
    """Renders the register page"""
    form = RegisterForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data
        name = form.name.data

        add_user(email, password, name)
        send_confirmation_msg(form.email.data, form.name.data)

        return render_template('user/confirm.html', email=form.email.data, user=current_user)

    return render_template('user/register.html', form=form, user=current_user)


@blueprint.route("/login", methods=['GET', 'POST'])
def login() -> str or Response:
    """Renders the login page"""
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        user = get_user_by_email(email)
        login_user(user, remember=form.remember.data)
        return redirect(url_for('public.home'))

    return render_template('user/login.html', form=form, user=current_user)


@blueprint.route('/logout')
@login_required
def logout() -> Response:
    """Logouts user, redirects to homepage"""
    logout_user()
    return redirect(url_for('public.home'))


@blueprint.route('/confirm/<token>')
def confirm_email(token) -> str or Response:
    """Renders """
    try:
        email = confirm_token(token)
    except SignatureExpired or BadSignature:
        flash('The confirmation link is invalid or it has expired', 'danger')
    else:
        user = get_user_by_email(email)
        if user:
            if user.confirmed:
                flash('Account has already been confirmed', 'success')
            else:
                user.confirmed = True
                user.confirmed_on = dt.datetime.now()
                db.session.commit()
                flash('You have successfully confirmed your account', 'success')
        else:
            return abort(404)
    return render_template('user/confirm.html', email=None, user=current_user)


@blueprint.route('/settings')
@login_required
def settings() -> str:
    """Renders settings page"""
    return render_template('user/settings.html', user=current_user)
