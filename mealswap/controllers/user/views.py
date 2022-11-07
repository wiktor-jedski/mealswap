from flask import render_template, flash, redirect, url_for, Response, Blueprint, abort
from flask_login import login_user, login_required, logout_user, current_user
from mealswap.extensions import db
from mealswap.email import send_confirmation_msg
from mealswap.controllers.forms import RegisterForm, LoginForm, ChangePasswordForm, DeleteAccountForm, DietGoalPercentageForm, \
    DietGoalMacroForm
from .token import confirm_token, SignatureExpired, BadSignature
import datetime as dt
from mealswap.controllers.controls import add_user, get_user_by_email, set_password, delete_account, \
    set_diet_goals, get_settings_by_user

blueprint = Blueprint('user', __name__, static_folder='../static')


@blueprint.route('/register', methods=['GET', 'POST'])
def register() -> str or Response:
    """Renders the register page

    :return: rendered register template OR
        rendered confirm template if register form validated
    """
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
    """Renders the login page

    :return: rendered login page OR
        redirect to home page if form validated
    """
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
    """Logouts user, redirects to homepage

    :return: redirect to home page
    """
    logout_user()
    return redirect(url_for('public.home'))


@blueprint.route('/confirm/<token>')
def confirm_email(token: str) -> str or Response:
    """Renders email confirmation page

    :param token: token generated in the confirmation message during register
    :return: rendered confirm template
    """
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


@blueprint.route('/settings', methods=['GET', 'POST'])
@login_required
def settings() -> str or Response:
    """Renders settings page

    :return: rendered settings template OR
        redirect to settings if changed password, updated diet goals OR
        redirect to home page if user deleted account
    """

    current_settings = get_settings_by_user(current_user)

    change_password_form = ChangePasswordForm(current_user)
    if change_password_form.validate_on_submit():
        set_password(current_user, change_password_form.new_password.data)
        flash("Password changed.")
        return redirect(url_for('user.settings'))

    delete_form = DeleteAccountForm(current_user)
    if delete_form.validate_on_submit():
        logout_user()
        delete_account(current_user)
        return redirect(url_for('public.home'))

    diet_goal_percentage_form = DietGoalPercentageForm()
    if diet_goal_percentage_form.validate_on_submit():
        calories = diet_goal_percentage_form.calories.data
        protein_percent = diet_goal_percentage_form.protein.data
        carb_percent = diet_goal_percentage_form.carb.data
        fat_percent = diet_goal_percentage_form.fat.data
        set_diet_goals(current_user, calories, protein_percent, carb_percent, fat_percent, percentage=True)
        flash("Diet goals updated successfully.")
        return redirect(url_for('user.settings'))

    diet_goal_macro_form = DietGoalMacroForm()
    if diet_goal_macro_form.validate_on_submit():
        calories = diet_goal_macro_form.calories.data
        protein = diet_goal_macro_form.protein.data
        carb = diet_goal_macro_form.carb.data
        fat = diet_goal_macro_form.fat.data
        set_diet_goals(current_user, calories, protein, carb, fat, percentage=False)
        flash("Diet goals updated successfully.")
        return redirect(url_for('user.settings'))
    # populate the form if data exists
    if current_settings.calories_goal:
        diet_goal_macro_form.calories.data = current_settings.calories_goal
    if current_settings.protein_goal:
        diet_goal_macro_form.protein.data = current_settings.protein_goal
    if current_settings.carb_goal:
        diet_goal_macro_form.carb.data = current_settings.carb_goal
    if current_settings.fat_goal:
        diet_goal_macro_form.fat.data = current_settings.fat_goal

    return render_template('user/settings.html', user=current_user, change_password_form=change_password_form,
                           delete_form=delete_form, diet_goal_percentage_form=diet_goal_percentage_form,
                           diet_goal_macro_form=diet_goal_macro_form)
