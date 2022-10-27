from flask import Blueprint, Response, redirect, url_for, render_template, request, flash, session
from flask_login import current_user, login_required
from mealswap.forms import SearchForm, DiscoverForm
from mealswap.extensions import login_manager
from mealswap.controller.controls import Model, get_element_by_id, get_element_list_by_ids, set_rating, \
    get_saved_items, get_ratings_by_user, get_saved_items_by_name
from random import randrange

blueprint = Blueprint('rate', __name__, static_folder='../static')


@login_manager.user_loader
def load_user(user_id):
    return get_element_by_id(Model.USER, user_id)


@blueprint.route('/rate', methods=['GET', 'POST'])
@login_required
def rate() -> str or Response:
    """Renders instruction page for rating."""
    search_form = SearchForm()
    if search_form.validate_on_submit() and search_form.submitSearchForm.data:
        search_str = search_form.search.data
        return redirect(url_for('rate.rate_search', searched=search_str))

    discover_form = DiscoverForm()
    if discover_form.validate_on_submit() and discover_form.submitDiscoverForm.data:
        return redirect(url_for('rate.rate_discover'))

    return render_template('rate/rate.html', user=current_user, search_form=search_form, discover_form=discover_form)


@blueprint.route('/rate/<searched>')
@login_required
def rate_search(searched) -> str:
    """Renders results for searching meals to be rated."""
    items_searched = get_saved_items_by_name(searched)
    assoc_items_rated = get_ratings_by_user(current_user)

    items_rated = [assoc.item for assoc in assoc_items_rated]
    items = [item for item in items_searched if item not in items_rated]

    return render_template('rate/rate_search.html', user=current_user, items=items, searched=searched)


@blueprint.route('/rate/discover')
@login_required
def rate_discover():
    """Renders a random meal to be rated."""
    items = session.get('rateable_items')
    if items:
        items = get_element_list_by_ids(Model.ITEM, items)
    else:
        items = get_saved_items()
        items_rated = get_ratings_by_user(current_user)
        for assoc in items_rated:
            try:
                items.remove(assoc.item)
            except ValueError:
                continue
        rateable_items = [item.id for item in items]
        session['rateable_items'] = rateable_items

    if items:
        item = items[randrange(len(items))]
    else:
        item = None
    return render_template('rate/rate_discover.html', user=current_user, item=item)


@blueprint.route('/rate/commit')
@login_required
def rate_commit() -> Response:
    """Adds rating for the meal and returns the user to previous directory."""
    rating = request.args.get('rating')
    item_id = request.args.get('item_id')
    searched = request.args.get('searched')
    edit = request.args.get('edit')

    item = get_element_by_id(Model.ITEM, item_id)
    item_name = set_rating(item, current_user, rating)

    if edit:
        flash(message=f"Rating for: '{item_name}' successfully updated!", category="success")
        return redirect(url_for('edit.edit_ratings'))

    if searched:
        return redirect(url_for('rate.rate_search', searched=searched))
    else:
        session['rateable_items'] = session['rateable_items'].remove(int(item_id))
        return redirect(url_for('rate.rate_discover'))
