from flask import render_template, abort, flash, redirect, url_for, Response, Blueprint
from flask_login import login_user, login_required, logout_user
from werkzeug.security import generate_password_hash
from mealswap.extensions import login_manager, db
from mealswap.user.models import User
from forms import RegisterForm, LoginForm

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
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('confirm_email'))
    else:
        for error in form.errors:
            flash(error)
    return render_template('user/register.html', form=form)


@blueprint.route("/login", methods=['GET', 'POST'])
def login() -> str or Response:
    """Renders the login page"""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        login_user(user)
        return redirect(url_for('home'))
    else:
        for error in form.errors:
            flash(error)
    return render_template('user/login.html', form=form)


@blueprint.route('/logout')
@login_required
def logout() -> Response:
    """Logouts user, redirects to homepage"""
    logout_user()
    return redirect(url_for('public.home'))
