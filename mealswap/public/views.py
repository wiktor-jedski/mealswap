from flask import render_template, Blueprint, redirect, url_for, flash, Response
from flask_login import current_user
from mealswap.user.forms import DateForm
from mealswap.extensions import login_manager, db
from mealswap.models import User, Product, Item
from mealswap.public.forms import ProductForm, EmptyMealForm, CompositeMealForm

blueprint = Blueprint('public', __name__, static_folder='../static')


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=int(user_id)).first()


@blueprint.route("/")
def home() -> str:
    """Renders the homepage.
    Homepage looks differently, depending on the login status:
    - logged in: calendar view for the current user and search
    - logged out: call to action"""
    if current_user.is_active:
        form = DateForm()
        return render_template('user/calendar.html', user=current_user, form=form)
    else:
        return render_template('public/home.html', user=current_user)


@blueprint.route("/search")
def search() -> str:
    """Renders meal replacement search."""
    return render_template('public/search.html', user=current_user)


@blueprint.route("/contact")
def contact() -> str:
    """Renders contact info."""
    return render_template('public/contact.html', user=current_user)


@blueprint.route("/add_product", methods=['GET', 'POST'])
def add_product() -> str or Response:
    """Renders form for adding products."""
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(
            name=form.name.data,
            protein=form.protein.data,
            carb=form.carb.data,
            fat=form.fat.data
        )
        item = Item(
            name=form.name.data,
            protein=form.protein.data,
            carb=form.carb.data,
            fat=form.fat.data
        )
        db.session.add(product)
        item.products.append(product)
        db.session.add(item)
        db.session.commit()

        flash(f'Product "{form.name.data}" successfully added!', category='success')
        return redirect(url_for('public.add_product'))
    return render_template('public/add_product.html', user=current_user, form=form)


@blueprint.route("/add_meal", methods=['GET', 'POST'])
def add_meal() -> str or Response:
    """Renders form for adding meals."""
    empty_meal_form = EmptyMealForm()
    composite_meal_form = CompositeMealForm()
    if empty_meal_form.validate_on_submit():
        item = Item(
            name=empty_meal_form.name.data,
            protein=empty_meal_form.protein.data,
            carb=empty_meal_form.protein.data,
            fat=empty_meal_form.fat.data,
            link=empty_meal_form.link.data,
            recipe=empty_meal_form.recipe.data
        )
        db.session.add(item)
        db.session.commit()

        flash(f'Meal "{empty_meal_form.name.data}" successfully added!', category='success')
        return redirect(url_for('public.add_meal'))
    # TODO: implement adding meal composed of products
    return render_template('public/add_meal.html', user=current_user,
                           empty_meal_form=empty_meal_form, composite_meal_form=composite_meal_form)
