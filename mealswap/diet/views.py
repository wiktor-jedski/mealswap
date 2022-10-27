from flask import Blueprint, redirect, url_for, request, render_template, Response, flash
from flask_login import login_required, current_user
from mealswap.extensions import login_manager
from mealswap.controller.controls import Model, get_element_by_id, get_saved_items, get_diet_by_date, add_diet, \
    delete_diet, edit_item_qty_in_diet, delete_item_in_diet, add_item_to_diet, get_saved_items_by_name
from mealswap.forms import DateForm, SearchForm, DeleteForm, EditForm, QtyForm, QtyEaForm, EaEditForm

blueprint = Blueprint('diet', __name__, static_folder='../static')


@login_manager.user_loader
def load_user(user_id):
    return get_element_by_id(Model.USER, user_id)


@blueprint.route("/calendar", methods=['GET', 'POST'])
@login_required
def calendar():
    """Starting page for looking up diet"""
    date_form = DateForm()
    if date_form.validate_on_submit():
        date = date_form.date.data
        return redirect(url_for('diet.day', date=date))
    return render_template('diet/calendar.html', user=current_user, form=date_form)


@blueprint.route('/day/<date>', methods=['GET', 'POST'])
@login_required
def day(date):
    """Renders the diet for the day"""
    diet = get_diet_by_date(date)
    total = {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0}

    if diet:
        for a in diet.items:
            if a.item.has_weight:
                total['calories'] += a.item.calories * a.qty / 100
                total['protein'] += a.item.protein * a.qty / 100
                total['carbs'] += a.item.carb * a.qty / 100
                total['fat'] += a.item.fat * a.qty / 100
            else:
                total['calories'] += a.item.calories * a.qty
                total['protein'] += a.item.protein * a.qty
                total['carbs'] += a.item.carb * a.qty
                total['fat'] += a.item.fat * a.qty

    copy_form = DateForm()
    if copy_form.validate_on_submit():
        copy_date = copy_form.date.data
        copied = get_diet_by_date(copy_date)
        if copied:
            if diet is None:
                diet = add_diet(user=current_user, date=date)
            copy_date(copied=copied, diet=diet)
            return redirect(url_for('diet.day', date=date))

    search_form = SearchForm()
    if search_form.validate_on_submit():
        search_str = search_form.search.data
        return redirect(url_for('diet.diet_search', searched=search_str, date=date))

    delete_form = DeleteForm()
    if delete_form.validate_on_submit():
        delete_diet(diet)
        return redirect(url_for('diet.day', date=date))

    edit_form = EditForm()
    if edit_form.validate_on_submit():
        request_list = list(request.form)
        request_list.remove('qty')
        request_list.remove('csrf_token')
        assoc_id = request_list[0]

        assoc = get_element_by_id(Model.DIET_ITEM, assoc_id)
        edit_item_qty_in_diet(assoc, new_qty=edit_form.qty.data)
        
        return redirect(url_for('diet.day', date=date))

    ea_edit_form = EaEditForm()
    if ea_edit_form.validate_on_submit():
        request_list = list(request.form)
        request_list.remove('qty')
        request_list.remove('csrf_token')
        assoc_id = request_list[0]

        assoc = get_element_by_id(Model.DIET_ITEM, assoc_id)
        edit_item_qty_in_diet(assoc, new_qty=ea_edit_form.qty.data)

        return redirect(url_for('diet.day', date=date))

    return render_template('diet/day.html',
                           user=current_user, date=date, diet=diet, total=total, edit_form=edit_form,
                           date_form=copy_form, search_form=search_form, delete_form=delete_form,
                           ea_edit_form=ea_edit_form)


@blueprint.route('/day/delete')
@login_required
def delete_item_in_day() -> Response:
    """Deletes the position from the diet for the date."""
    assoc_id = request.args.get('assoc_id')
    diet_id = request.args.get('diet_id')
    date = request.args.get('date')

    assoc = get_element_by_id(Model.DIET_ITEM, assoc_id)
    diet = get_element_by_id(Model.DAY, diet_id)
    delete_item_in_diet(assoc, diet)
    
    if not diet.items:
        delete_diet(diet)

    return redirect(url_for('diet.day', date=date))


@blueprint.route("/day/<date>/add/<searched>", methods=['GET', 'POST'])
@login_required
def diet_search(searched, date) -> str or Response:
    """Renders search results for string"""
    items = get_saved_items_by_name(searched)
    form = QtyEaForm()
    if request.method == 'POST':
        request_list = list(request.form)
        request_list.remove('csrf_token')
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
        item_id = request_list[0]
        
        item = get_element_by_id(Model.ITEM, item_id)
        diet = get_diet_by_date(date)

        # anonymous form validation
        if qty is None and ea is None:
            flash("Either qty in grams or ea has to be filled.")
            return redirect(url_for('diet.diet_search', searched=searched, date=date))
        if qty and ea:
            flash("Please fill only one field - either qty in grams or ea.")
            return redirect(url_for('diet.diet_search', searched=searched, date=date))

        if diet is None:
            diet = add_diet(user=current_user, date=date)

        add_item_to_diet(item, qty, ea, diet)
        
        return redirect(url_for('diet.day', date=date))
    return render_template('diet/diet_search.html',
                           user=current_user, items=items, date=date, searched=searched, form=form)
