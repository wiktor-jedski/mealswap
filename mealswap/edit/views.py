from flask import render_template, Blueprint, Response, redirect, url_for
from flask_login import login_required, current_user
from mealswap.controller.controls import get_element_by_id, Model, get_open_items_by_user, get_ratings_by_user, \
    get_saved_items_by_name, delete_meal_from_db
from mealswap.extensions import login_manager
from mealswap.forms import SearchForm

blueprint = Blueprint('edit', __name__, static_folder='../static')


@login_manager.user_loader
def load_user(user_id):
    return get_element_by_id(Model.USER, user_id)


@blueprint.route('/edit_meals')
@login_required
def edit_meals() -> str:
    """Renders open meals available for editing."""
    items = get_open_items_by_user(current_user)
    return render_template('edit/edit_meals.html', user=current_user, items=items)


@blueprint.route('/edit_meals/delete/<item_id>')
@login_required
def delete_meal(item_id) -> Response:
    """Deletes open meal from database."""
    item = get_element_by_id(Model.ITEM, item_id)
    delete_meal_from_db(item)
    return redirect(url_for('edit.edit_meals'))


@blueprint.route('/edit_ratings', methods=['GET', 'POST'])
@login_required
def edit_ratings() -> str or Response:
    """Renders ratings for meals with an option to change them."""
    search_form = SearchForm()
    if search_form.validate_on_submit() and search_form.submitSearchForm.data:
        search_str = search_form.search.data
        return redirect(url_for('edit.edit_ratings_search', searched=search_str))

    return render_template('edit/edit_ratings.html', user=current_user, search_form=search_form)


@blueprint.route('/edit_ratings/<searched>')
@login_required
def edit_ratings_search(searched: str) -> str or Response:
    """Renders results for searching ratings to be edited."""
    items_searched = get_saved_items_by_name(searched)
    assoc_items_rated = get_ratings_by_user(current_user)

    items = [(assoc.rating, assoc.item) for assoc in assoc_items_rated if assoc.item in items_searched]

    return render_template('edit/edit_ratings_search.html', user=current_user, items=items, searched=searched)
