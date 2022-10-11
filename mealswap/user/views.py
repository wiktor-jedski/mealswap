from flask import render_template, flash, redirect, url_for, Response, Blueprint, request
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash
from mealswap.extensions import login_manager, db
from mealswap.email import send_confirmation_msg
from mealswap.models import User, DayDiet, Item, DietItemAssoc
from .forms import RegisterForm, LoginForm, DateForm, SearchForm, QtyForm, DeleteForm, EditForm
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


@blueprint.route('/day/<date>', methods=['GET', 'POST'])
@login_required
def day(date):
    """Renders the diet for the day"""
    diet = DayDiet.query.filter_by(date=date).first()
    total = {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0}

    if diet:
        for a in diet.items:
            total['calories'] += a.item.calories * a.qty / 100
            total['protein'] += a.item.protein * a.qty / 100
            total['carbs'] += a.item.carb * a.qty / 100
            total['fat'] += a.item.fat * a.qty / 100

    date_form = DateForm()
    if date_form.validate_on_submit():
        copy_date = date_form.date.data
        copy_diet = DayDiet.query.filter_by(date=copy_date).first()
        if copy_diet:
            if diet is None:
                date = dt.datetime.strptime(date, "%Y-%m-%d").date()
                diet = DayDiet(user=current_user,
                               date=date)
                db.session.add(diet)
            for a in copy_diet.items:
                new_a = DietItemAssoc(qty=a.qty)
                new_a.item = a.item
                diet.items.append(new_a)
            db.session.commit()
            return redirect(url_for('user.day', date=date))

    search_form = SearchForm()
    if search_form.validate_on_submit():
        search_str = search_form.search.data
        return redirect(url_for('user.add_search', searched=search_str, date=date))

    delete_form = DeleteForm()
    if delete_form.validate_on_submit():
        while diet.items:
            assoc = diet.items.pop()
            db.session.delete(assoc)
        db.session.commit()
        return redirect(url_for('user.day', date=date))

    edit_form = EditForm()
    if edit_form.validate_on_submit():
        request_list = list(request.form)
        request_list.remove('qty')
        request_list.remove('csrf_token')
        index = request_list[0]

        assoc = db.session.query(DietItemAssoc).get(index)
        assoc.qty = edit_form.qty.data
        db.session.commit()
        return redirect(url_for('user.day', date=date))

    return render_template('user/day.html',
                           user=current_user, date=date, diet=diet, total=total, edit_form=edit_form,
                           date_form=date_form, search_form=search_form, delete_form=delete_form)


@blueprint.route('/day/delete')
@login_required
def delete_item_in_day() -> Response:
    """Deletes the position from the diet for the date."""
    index = request.args.get('index')
    diet_id = request.args.get('diet_id')
    date = request.args.get('date')

    assoc = DietItemAssoc.query.filter_by(index=index).first()
    diet = DayDiet.query.filter_by(id=diet_id).first()

    diet.items.remove(assoc)
    db.session.delete(assoc)
    db.session.commit()

    return redirect(url_for('user.day', date=date))


@blueprint.route("/day/<date>/add/<searched>", methods=['GET', 'POST'])
@login_required
def add_search(searched, date) -> str or Response:
    """Renders search results for string"""
    items = Item.query.filter(Item.name.contains(searched), Item.saved == True)
    form = QtyForm()
    if request.method == 'POST':
        diet = DayDiet.query.filter_by(date=date).first()
        request_list = list(request.form)
        request_list.remove('qty')
        request_list.remove('csrf_token')
        item_id = request_list[0]
        item = Item.query.filter_by(id=item_id).first()

        if diet is None:
            date = dt.datetime.strptime(date, "%Y-%m-%d").date()
            diet = DayDiet(user=current_user,
                           date=date)
            db.session.add(diet)

        assoc = DietItemAssoc(qty=form.qty.data)
        assoc.item = item
        diet.items.append(assoc)

        db.session.commit()
        return redirect(url_for('user.day', date=date))
    return render_template('user/add_search.html',
                           user=current_user, items=items, date=date, searched=searched, form=form)
