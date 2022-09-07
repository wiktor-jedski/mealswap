from flask import render_template, flash, redirect, url_for, Response, Blueprint
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash
from mealswap.extensions import login_manager, db
from mealswap.email import send_confirmation_msg
from mealswap.models import User
from .forms import RegisterForm, LoginForm
from .token import confirm_token, SignatureExpired, BadSignature
import datetime as dt

blueprint = Blueprint('user', __name__, static_folder='../static')


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=int(user_id)).first()


@blueprint.route('/register', methods=['GET', 'POST'])
def register() -> str or Response:
    """Renders the register page"""
    form = RegisterForm()
    if form.validate_on_submit():
        new_user = User(
            email=form.email.data,
            password=generate_password_hash(form.password.data),
            name=form.name.data,
            confirmed=False
        )

        send_confirmation_msg(form.email.data, form.name.data)

        db.session.add(new_user)
        db.session.commit()

        return render_template('user/confirm.html', email=form.email.data, user=current_user)
    else:
        for error in form.errors:
            flash(error)
    return render_template('user/register.html', form=form, user=current_user)


@blueprint.route("/login", methods=['GET', 'POST'])
def login() -> str or Response:
    """Renders the login page"""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        login_user(user, remember=form.remember.data)
        return redirect(url_for('public.home'))
    else:
        for error in form.errors:
            flash(error)
    return render_template('user/login.html', form=form, user=current_user)


@blueprint.route('/logout')
@login_required
def logout() -> Response:
    """Logouts user, redirects to homepage"""
    logout_user()
    return redirect(url_for('public.home'))


@blueprint.route('/confirm/<token>')
def confirm_email(token):
    try:
        email = confirm_token(token)
    except SignatureExpired or BadSignature:
        flash('The confirmation link is invalid or it has expired', 'danger')
    else:
        user = User.query.filter_by(email=email).first_or_404()
        if user.confirmed:
            flash('Account has already been confirmed', 'success')
        else:
            user.confirmed = True
            user.confirmed_on = dt.datetime.now()
            db.session.commit()
            flash('You have successfully confirmed your account', 'success')
    return render_template('user/confirm.html', email=None, user=current_user)
