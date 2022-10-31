from flask import Blueprint, Response, redirect, url_for, render_template, flash, abort, request
from flask_login import current_user, login_required
from mealswap.controller.controls import add_product_to_db, get_element_by_id, Model, add_meal_to_db, set_meal_recipe, \
    set_qty_in_meal, clear_meal, save_meal, get_products_by_name, add_product_to_meal, copy_meal, \
    delete_index_from_meal, get_saved_composed_items_by_name
from mealswap.extensions import login_manager
from mealswap.forms import ProductForm, WeightMealForm, CompositeMealForm, LinkRecipeServingsForm, CopyMealForm, \
    SearchForm, EditForm, DeleteForm, SaveForm, ServingMealForm, QtyEaForm

blueprint = Blueprint('add', __name__, static_folder='../static')


@login_manager.user_loader
def load_user(user_id):
    return get_element_by_id(Model.USER, user_id)


@blueprint.route("/add_product", methods=['GET', 'POST'])
@login_required
def add_product() -> str or Response:
    """Renders form for adding products."""
    form = ProductForm()
    if form.validate_on_submit() and form.submitProductForm.data:
        name = add_product_to_db(form.name.data, form.protein.data, form.carb.data, form.fat.data, current_user,
                                 weight_per_ea=form.weight_per_ea.data)

        flash(f'Product "{name}" successfully added!', category='success')
        return redirect(url_for('add.add_product'))
    return render_template('add/add_product.html', user=current_user, form=form)


@blueprint.route("/add_meal", methods=['GET', 'POST'])
@login_required
def add_meal() -> str or Response:
    """Renders form for adding meals."""
    weight_meal_form = WeightMealForm()
    if weight_meal_form.validate_on_submit() and weight_meal_form.submitWeightMealForm.data:
        has_weight = True
        qty = weight_meal_form.qty.data
        if qty:
            servings = 1
        else:
            servings = 0
        item = add_meal_to_db(weight_meal_form.name.data, weight_meal_form.protein.data, weight_meal_form.carb.data,
                              weight_meal_form.fat.data, current_user, has_weight, weight_meal_form.link.data,
                              weight_meal_form.recipe.data, saved=True, qty=qty, servings=servings)

        flash(f'Meal "{item.name}" successfully added!', category='success')
        return redirect(url_for('add.add_meal'))

    serving_meal_form = ServingMealForm()
    if serving_meal_form.validate_on_submit() and serving_meal_form.submitServingMealForm.data:
        has_weight = False
        item = add_meal_to_db(serving_meal_form.name.data, serving_meal_form.protein.data, serving_meal_form.carb.data,
                              serving_meal_form.fat.data, current_user, has_weight, serving_meal_form.link.data,
                              serving_meal_form.recipe.data, saved=True, qty=1, servings=1)

        flash(f'Meal "{item.name}" successfully added!', category='success')
        return redirect(url_for('add.add_meal'))

    composite_meal_form = CompositeMealForm()
    if composite_meal_form.validate_on_submit() and composite_meal_form.submitCompositeMealForm.data:
        has_weight = True
        item = add_meal_to_db(composite_meal_form.name.data, 0, 0, 0, current_user, has_weight,
                              composite_meal_form.link.data, composite_meal_form.recipe.data, saved=False,
                              qty=0, servings=1)

        return redirect(url_for('add.compose_meal', item_id=item.id))

    return render_template('add/add_meal.html', user=current_user, weight_meal_form=weight_meal_form,
                           serving_meal_form=serving_meal_form, composite_meal_form=composite_meal_form)


@blueprint.route("/compose_meal/<item_id>", methods=['GET', 'POST'])
@login_required
def compose_meal(item_id) -> str or Response:
    """Renders form for composing meals."""
    item = get_element_by_id(Model.ITEM, item_id)
    # prevent user from accessing a saved meal or another user's meal
    if item.saved or item.user != current_user:
        return abort(code=412)

    # update link and/or recipe
    link_recipe_form = LinkRecipeServingsForm()
    if link_recipe_form.validate_on_submit() and link_recipe_form.submitLinkRecipeForm.data:
        set_meal_recipe(item, link_recipe_form.link.data, link_recipe_form.recipe.data, link_recipe_form.servings.data)
        return redirect(url_for('add.compose_meal', item_id=item_id))
    link_recipe_form.link.data = item.link
    link_recipe_form.recipe.data = item.recipe
    link_recipe_form.servings.data = item.servings

    # create a copy of another meal
    copy_form = CopyMealForm()
    if copy_form.validate_on_submit() and copy_form.submitCopyMealForm.data:
        search_str = copy_form.search.data
        return redirect(url_for('add.compose_copy', searched=search_str, item_id=item_id))

    # search for products to add
    search_form = SearchForm()
    if search_form.validate_on_submit() and search_form.submitSearchForm.data:
        search_str = search_form.search.data
        return redirect(url_for('add.compose_search', searched=search_str, item_id=item.id))

    # edit qty for an item
    edit_form = EditForm()
    if edit_form.validate_on_submit():
        request_list = list(request.form)
        request_list.remove('qty')
        request_list.remove('csrf_token')
        index = request_list[0]
        new_qty = edit_form.qty.data

        assoc = get_element_by_id(Model.ITEM_PRODUCT, index)
        set_qty_in_meal(assoc, item, new_qty)
        return redirect(url_for('add.compose_meal', item_id=item_id))

    # delete all items
    delete_form = DeleteForm()
    if delete_form.validate_on_submit() and delete_form.submitDeleteForm.data:
        clear_meal(item)
        return redirect(url_for('add.compose_meal', item_id=item_id))

    # save meal and close for edits
    save_form = SaveForm()
    if save_form.validate_on_submit() and save_form.submitSaveForm.data:
        save_meal(item)
        return redirect(url_for('add.add_meal'))

    return render_template('add/compose_meal.html', edit_form=edit_form, copy_form=copy_form, save_form=save_form,
                           delete_form=delete_form, user=current_user, item=item, search_form=search_form,
                           link_recipe_form=link_recipe_form)


@blueprint.route("/compose_meal/<item_id>/<searched>", methods=['GET', 'POST'])
@login_required
def compose_search(item_id, searched) -> str or Response:
    """Renders search result for adding products to composed meals."""
    products = get_products_by_name(searched)
    form = QtyEaForm()
    if request.method == 'POST':
        request_list = list(request.form)
        request_list.remove('qty')
        request_list.remove('csrf_token')
        try:
            request_list.remove('ea')
        except ValueError:
            pass
        product_id = request_list[0]

        item = get_element_by_id(Model.ITEM, item_id)
        product = get_element_by_id(Model.PRODUCT, product_id)

        # anonymous form validation
        if not form.qty.data and not form.ea.data:
            flash("Either qty in grams or ea has to be filled.")
            return redirect(url_for('add.compose_search', item_id=item_id, searched=searched))
        elif form.qty.data and form.ea.data:
            flash("Please fill only one field - either qty in grams or ea.")
            return redirect(url_for('add.compose_search', item_id=item_id, searched=searched))
        elif form.qty.data:
            add_product_to_meal(item, product, form.qty.data)
        else:
            add_product_to_meal(item, product, form.ea.data*product.weight_per_ea)

        return redirect(url_for('add.compose_meal', item_id=item_id))
    return render_template('add/compose_search.html',
                           user=current_user, products=products, searched=searched, form=form)


@blueprint.route("/compose_meal/<item_id>/copy/<searched>", methods=['GET', 'POST'])
@login_required
def compose_copy(item_id, searched) -> str or Response:
    """Renders search results for copying existing meals."""
    items = get_saved_composed_items_by_name(searched)
    if request.method == 'POST':
        request_list = list(request.form)
        copy_item_id = request_list[0]

        copy_item = get_element_by_id(Model.ITEM, copy_item_id)
        item = get_element_by_id(Model.ITEM, item_id)
        copy_meal(item, copy_item)

        return redirect(url_for('add.compose_meal', item_id=item_id))

    return render_template('add/compose_copy.html', user=current_user, items=items, searched=searched)


@blueprint.route('/compose_meal/delete_pos')
@login_required
def delete_product_in_meal() -> Response:
    """Deletes the position from the meal"""
    assoc_id = request.args.get('assoc_id')
    item_id = request.args.get('item_id')

    item = get_element_by_id(Model.ITEM, item_id)
    assoc = get_element_by_id(Model.ITEM_PRODUCT, assoc_id)
    delete_index_from_meal(item, assoc)

    return redirect(url_for('add.compose_meal', item_id=item_id))
