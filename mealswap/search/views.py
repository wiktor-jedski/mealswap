import sqlalchemy.exc
from flask import Blueprint, render_template, Response, redirect, url_for, request, flash, session
from flask_login import current_user, login_required
from mealswap.extensions import login_manager
from mealswap.forms import SearchForm, MacroForm, DiscoverForm, DateQtyEaForm
from mealswap.controller.controls import get_element_by_id, Model, get_saved_items_by_name, get_saved_items, \
    get_diet_by_date, add_diet, add_item_to_diet, get_element_list_by_ids
from .helpers import get_float, get_similar_items, get_predictions

blueprint = Blueprint('search', __name__, static_folder='../static')


@login_manager.user_loader
def load_user(user_id):
    return get_element_by_id(Model.USER, user_id)


@blueprint.route("/search", methods=['GET', 'POST'])
@login_required
def search() -> str or Response:
    """Renders meal replacement search."""
    name_form = SearchForm()
    if name_form.validate_on_submit() and name_form.submitSearchForm.data:
        search_str = name_form.search.data
        return redirect(url_for('search.search_replace', searched=search_str))

    macro_form = MacroForm()
    if macro_form.validate_on_submit() and macro_form.submitMacroForm.data:
        protein = macro_form.protein.data
        carb = macro_form.carb.data
        fat = macro_form.fat.data
        calories = macro_form.calories.data
        return redirect(url_for('search.search_macro', protein=protein, carb=carb, fat=fat, calories=calories))

    discover_form = DiscoverForm()
    if discover_form.validate_on_submit() and discover_form.submitDiscoverForm.data:
        return redirect(url_for('search.search_discover'))

    return render_template('search/search.html',
                           user=current_user, name_form=name_form, macro_form=macro_form, discover_form=discover_form)


@blueprint.route("/search/str/<searched>", methods=['GET', 'POST'])
@login_required
def search_replace(searched) -> str or Response:
    """Renders results for searching replacement by name."""
    items = get_saved_items_by_name(searched)
    if request.method == 'POST':
        request_list = list(request.form)
        item_id = request_list[0]
        return redirect(url_for('search.search_macro', item_id=item_id))
    return render_template('search/search_replace.html', user=current_user, searched=searched, items=items)


@blueprint.route("/search/replacement", methods=['GET', 'POST'])
def search_macro() -> str or Response:
    """Renders results for searching replacement by macronutrients."""
    items = get_saved_items()
    item_id = request.args.get('item_id', default=None)

    if item_id:
        item = get_element_by_id(Model.ITEM, item_id)
        name = item.name
        items.remove(item)
        protein = item.protein
        carb = item.carb
        fat = item.fat
        calories = item.calories
    else:
        name = None
        protein = get_float('protein')
        carb = get_float('carb')
        fat = get_float('fat')
        calories = get_float('calories')

    similarity_list = get_similar_items(items, protein, carb, fat, calories, item_id)

    form = DateQtyEaForm()
    if request.method == 'POST':
        request_list = list(request.form)
        request_list.remove('csrf_token')
        request_list.remove('date')
        try:
            request_list.remove('qty')
            qty = form.qty.data
        except ValueError:
            qty = None
        try:
            request_list.remove('ea')
            ea = form.ea.data
        except ValueError:
            ea = None
        item_added_id = request_list[0]
        date = form.date.data

        item_added = get_element_by_id(Model.ITEM, item_added_id)
        diet = get_diet_by_date(date)

        # anonymous form validation
        if qty is None and ea is None:
            flash("Either qty in grams or ea has to be filled.")
            if item_id:
                return redirect(url_for('search.search_macro', item_id=item_id))
            else:
                return redirect(url_for('search.search_macro', protein=protein, carb=carb, fat=fat, calories=calories))
        if qty and ea:
            flash("Please fill only one field - either qty in grams or ea.")
            if item_id:
                return redirect(url_for('search.search_macro', item_id=item_id))
            else:
                return redirect(url_for('search.search_macro', protein=protein, carb=carb, fat=fat, calories=calories))

        if diet is None:
            diet = add_diet(user=current_user, date=date)

        add_item_to_diet(item_added, qty, ea, diet)

        return redirect(url_for('diet.day', date=date))

    return render_template('search/search_macro.html',
                           user=current_user, items=similarity_list, form=form,
                           name=name, protein=protein, carb=carb, fat=fat, calories=calories)


@blueprint.route("/search/discover", methods=['GET', 'POST'])
@login_required
def search_discover() -> str or Response:
    """Renders results for searching replacement by ratings."""
    try:
        items = get_element_list_by_ids(Model.ITEM, session.get('prediction_items'))
    except sqlalchemy.exc.ArgumentError:
        items = get_predictions(current_user)
        prediction_items = [item.id for item in items]
        session['prediction_items'] = prediction_items

    form = DateQtyEaForm()
    if request.method == 'POST':
        request_list = list(request.form)
        request_list.remove('csrf_token')
        request_list.remove('date')
        try:
            request_list.remove('qty')
            qty = form.qty.data
        except ValueError:
            qty = None
        try:
            request_list.remove('ea')
            ea = form.ea.data
        except ValueError:
            ea = None
        item_added_id = request_list[0]
        date = form.date.data

        item_added = get_element_by_id(Model.ITEM, item_added_id)
        diet = get_diet_by_date(date)

        # anonymous form validation
        if qty is None and ea is None:
            flash("Either qty in grams or ea has to be filled.")
            return redirect(url_for('search.search_discover'))
        if qty and ea:
            flash("Please fill only one field - either qty in grams or ea.")
            return redirect(url_for('search.search_discover'))

        if diet is None:
            diet = add_diet(user=current_user, date=date)

        add_item_to_diet(item_added, qty, ea, diet)

        return redirect(url_for('diet.day', date=date))

    return render_template('search/search_discover.html', user=current_user, items=items, form=form)
