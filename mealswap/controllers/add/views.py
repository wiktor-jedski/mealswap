from flask import Blueprint, Response, redirect, url_for, render_template, flash, abort, request
from flask_login import current_user, login_required
from mealswap.controllers.controls import add_product_to_db, get_element_by_id, Model, add_meal_to_db, set_meal_recipe, \
    set_qty_in_meal, clear_meal, save_meal, get_products_by_name, add_product_to_meal, copy_meal, \
    delete_index_from_meal, get_saved_composed_items_by_name
from mealswap.controllers.forms import ProductForm, WeightMealForm, CompositeMealForm, LinkRecipeServingsForm, CopyMealForm, \
    SearchForm, EditForm, DeleteForm, SaveForm, ServingMealForm, QtyEaForm

blueprint = Blueprint('add', __name__, static_folder='../static')


@blueprint.route("/add_product", methods=['GET', 'POST'])
@login_required
def add_product() -> str or Response:
    """Renders form for adding products.

    :return: rendered 'add_product' template or redirect to add_product after adding product
    """
    form = ProductForm()
    if form.validate_on_submit() and form.submitProductForm.data:
        product = add_product_to_db(form.name.data, form.protein.data, form.carb.data, form.fat.data, current_user,
                                    weight_per_ea=form.weight_per_ea.data)

        flash(f'Product "{product.name}" successfully added!', category='success')
        return redirect(url_for('add.add_product'))
    return render_template('add/add_product.html', user=current_user, form=form)


@blueprint.route("/add_meal", methods=['GET', 'POST'])
@login_required
def add_meal() -> str or Response:
    """Renders form for adding meals.

    :return: rendered add_meal template OR
        redirect to add_meal if added empty meal OR
        redirect to compose_meal if added composed meal
    """
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
def compose_meal(item_id: str) -> str or Response:
    """Renders form for composing meals.

    :param item_id: id of the composed meal
    :return: rendered compose_meal template OR
        error 403 if user should not access the meal OR
        redirect to compose_meal if added additional data/edited qty/deleted all items OR
        redirect to compose_copy if searched for a meal to copy OR
        redirect to compose_search if searched for a product to add OR
        redirect to add_meal if the current meal has been saved
    """
    item = get_element_by_id(Model.ITEM, item_id)
    # prevent user from accessing a saved meal or another user's meal
    if item.saved or item.user != current_user:
        return abort(code=403)

    # update link and/or recipe
    link_recipe_form = LinkRecipeServingsForm()
    if link_recipe_form.validate_on_submit() and link_recipe_form.submitLinkRecipeForm.data:
        set_meal_recipe(item, link_recipe_form.link.data, link_recipe_form.recipe.data, link_recipe_form.servings.data)
        flash("Optional data updated.", category='success')
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
        set_qty_in_meal(assoc, item, float(new_qty))
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
        flash(f'Meal "{item.name}" successfully added!', category='success')
        return redirect(url_for('add.add_meal'))

    return render_template('add/compose_meal.html', edit_form=edit_form, copy_form=copy_form, save_form=save_form,
                           delete_form=delete_form, user=current_user, item=item, search_form=search_form,
                           link_recipe_form=link_recipe_form)


@blueprint.route("/compose_meal/<item_id>/<searched>", methods=['GET', 'POST'])
@login_required
def compose_search(item_id: str, searched: str) -> str or Response:
    """Renders search result for adding products to composed meals.

    :param item_id: id of the composed meal
    :param searched: name or part of the name of the product for search query
    :return: rendered compose_search template OR
        redirect to compose_meal if the product has been added
    """
    page = request.args.get('page', 1, type=int)
    per_page = 5
    products = get_products_by_name(searched, paginate=True, page=page, per_page=per_page)
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
            flash("Either qty in grams or ea has to be filled.", category='error')
            return redirect(url_for('add.compose_search', item_id=item_id, searched=searched))
        elif form.qty.data and form.ea.data:
            flash("Please fill only one field - either qty in grams or ea.", category='error')
            return redirect(url_for('add.compose_search', item_id=item_id, searched=searched))
        elif form.qty.data:
            add_product_to_meal(item, product, float(form.qty.data))
        else:
            add_product_to_meal(item, product, float(form.ea.data)*product.weight_per_ea)

        return redirect(url_for('add.compose_meal', item_id=item_id))
    return render_template('add/compose_search.html',
                           user=current_user, pagination=products, searched=searched, form=form)


@blueprint.route("/compose_meal/<item_id>/copy/<searched>", methods=['GET', 'POST'])
@login_required
def compose_copy(item_id: str, searched: str) -> str or Response:
    """Renders search results for copying existing meals.

    :param item_id: id of the composed meal
    :param searched: name or part of the name of the copied meal for search query
    :return: rendered compose_copy template OR
        redirect to compose_meal if a meal has been chosen to copy
    """
    page = request.args.get('page', 1, type=int)
    per_page = 5
    items = get_saved_composed_items_by_name(searched, pagination=True, page=page, per_page=per_page)
    if request.method == 'POST':
        request_list = list(request.form)
        copy_item_id = request_list[0]

        copy_item = get_element_by_id(Model.ITEM, copy_item_id)
        item = get_element_by_id(Model.ITEM, item_id)
        copy_meal(item, copy_item)

        return redirect(url_for('add.compose_meal', item_id=item_id))

    return render_template('add/compose_copy.html', user=current_user, pagination=items, searched=searched)


@blueprint.route('/compose_meal/delete_pos')
@login_required
def delete_product_in_meal() -> Response:
    """Deletes the position from the meal.

    :return: redirect to compose_meal after deleting the product
    """
    assoc_id = request.args.get('assoc_id')
    item_id = request.args.get('item_id')

    item = get_element_by_id(Model.ITEM, item_id)
    assoc = get_element_by_id(Model.ITEM_PRODUCT, assoc_id)
    delete_index_from_meal(item, assoc)

    return redirect(url_for('add.compose_meal', item_id=item_id))
