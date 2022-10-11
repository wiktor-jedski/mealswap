from math import sqrt, acos, pi
from flask import render_template, Blueprint, redirect, url_for, flash, Response, request, abort
from flask_login import current_user, login_required
from mealswap.user.forms import DateForm
from mealswap.extensions import login_manager, db
from mealswap.models import User, Product, Item, ItemProductAssoc
from mealswap.public.forms import *

blueprint = Blueprint('public', __name__, static_folder='../static')


def get_float(key) -> float or None:
    """Helper function for getting arguments."""
    try:
        value = float(request.args.get(key))
    except TypeError:
        value = None
    return value


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=int(user_id)).first()


@blueprint.route("/", methods=['GET', 'POST'])
def home() -> str or Response:
    """Renders the homepage.
    Homepage looks differently, depending on the login status:
    - logged in: calendar view for the current user and search
    - logged out: call to action"""
    if current_user.is_active:
        form = DateForm()
        if form.validate_on_submit():
            day = form.date.data
            return redirect(url_for('user.day', date=day))
        return render_template('user/calendar.html', user=current_user, form=form)
    else:
        return render_template('public/home.html', user=current_user)


@blueprint.route("/search", methods=['GET', 'POST'])
def search() -> str or Response:
    """Renders meal replacement search."""
    name_form = SearchForm()
    if name_form.validate_on_submit():
        search_str = name_form.search.data
        return redirect(url_for('public.search_replace', searched=search_str))

    macro_form = MacroForm()
    if macro_form.validate_on_submit():
        protein = macro_form.protein.data
        carb = macro_form.carb.data
        fat = macro_form.fat.data
        calories = macro_form.calories.data
        return redirect(url_for('public.search_macro', protein=protein, carb=carb, fat=fat, calories=calories))

    discover_form = DiscoverForm()
    if discover_form.validate_on_submit():
        return redirect(url_for('public.search_discover'))

    return render_template('public/search.html',
                           user=current_user, name_form=name_form, macro_form=macro_form, discover_form=discover_form)


@blueprint.route("/search/str/<searched>", methods=['GET', 'POST'])
def search_replace(searched) -> str or Response:
    """Renders results for searching replacement by name."""
    items = Item.query.filter(Item.name.contains(searched))
    if request.method == 'POST':
        request_list = list(request.form)
        item_id = request_list[0]
        return redirect(url_for('public.search_macro', item_id=item_id))
    return render_template('public/search_replace.html', user=current_user, searched=searched, items=items)


@blueprint.route("/search/replacement", methods=['GET', 'POST'])
def search_macro() -> str:
    """Renders results for searching replacement by macros."""
    items = Item.query.all()
    item_id = request.args.get('item_id', default=None)
    if item_id:
        item = Item.query.filter_by(id=item_id).first()
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

    similarity_list = []
    for i in items:
        if item_id:
            numerator = i.protein * protein + \
                        i.carb * carb + \
                        i.fat * fat
            denominator = sqrt(i.protein * i.protein + i.carb * i.carb + i.fat * i.fat) * \
                          sqrt(protein * protein + carb * carb + fat * fat)
        else:
            numerator = 0
            den1 = 0
            den2 = 0
            if protein:
                numerator += i.protein * protein
                den1 += i.protein * i.protein
                den2 += protein * protein
            if carb:
                numerator += i.carb * carb
                den1 += i.carb * i.carb
                den2 += carb * carb
            if fat:
                numerator += i.fat * fat
                den1 += i.fat * i.fat
                den2 += fat * fat
            if calories:
                numerator += i.calories * calories
                den1 += i.calories * i.calories
                den2 += calories * calories
            denominator = sqrt(den1) * sqrt(den2)
        distance = acos(numerator / denominator)
        similarity = 1 - distance * 2 / pi
        similarity_list.append((similarity, i))
    similarity_list.sort(key=lambda x: x[0], reverse=True)

    form = DateQtyForm()

    return render_template('public/search_macro.html',
                           user=current_user, items=similarity_list, form=form,
                           name=name, protein=protein, carb=carb, fat=fat, calories=calories)


@blueprint.route("/search/discover")
def search_discover() -> str:
    """Renders results for searching replacement by ratings."""
    return render_template('public/search_discover.html', user=current_user)


@blueprint.route("/contact")
def contact() -> str:
    """Renders contact info."""
    return render_template('public/contact.html', user=current_user)


@blueprint.route("/add_product", methods=['GET', 'POST'])
@login_required
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
            fat=form.fat.data,
            user=current_user,
            saved=True
        )
        db.session.add(product)
        assoc = ItemProductAssoc(qty=100)
        assoc.product = product
        item.products.append(assoc)
        db.session.add(item)
        db.session.commit()

        flash(f'Product "{form.name.data}" successfully added!', category='success')
        return redirect(url_for('public.add_product'))
    return render_template('public/add_product.html', user=current_user, form=form)


@blueprint.route("/add_meal", methods=['GET', 'POST'])
@login_required
def add_meal() -> str or Response:
    """Renders form for adding meals."""
    empty_meal_form = EmptyMealForm()
    if empty_meal_form.validate_on_submit():
        item = Item(
            name=empty_meal_form.name.data,
            protein=empty_meal_form.protein.data,
            carb=empty_meal_form.protein.data,
            fat=empty_meal_form.fat.data,
            user=current_user,
            link=empty_meal_form.link.data,
            recipe=empty_meal_form.recipe.data,
            saved=True
        )
        db.session.add(item)
        db.session.commit()

        flash(f'Meal "{empty_meal_form.name.data}" successfully added!', category='success')
        return redirect(url_for('public.add_meal'))

    composite_meal_form = CompositeMealForm()
    if composite_meal_form.validate_on_submit():
        item = Item(
            name=composite_meal_form.name.data,
            protein=0,
            carb=0,
            fat=0,
            user=current_user,
            link=composite_meal_form.link.data,
            recipe=composite_meal_form.recipe.data
        )
        db.session.add(item)
        db.session.commit()
        return redirect(url_for('public.compose_meal', item_id=item.id))

    return render_template('public/add_meal.html', user=current_user,
                           empty_meal_form=empty_meal_form, composite_meal_form=composite_meal_form)


@blueprint.route("/compose_meal/<item_id>", methods=['GET', 'POST'])
@login_required
def compose_meal(item_id) -> str or Response:
    """Renders form for composing meals."""
    item = Item.query.filter_by(id=item_id).first()
    if item.saved:
        return abort(code=412)
    total = {'calories': item.calories, 'protein': item.protein, 'carbs': item.carb, 'fat': item.fat}

    copy_form = CopyMealForm()
    if copy_form.validate_on_submit() and copy_form.submitCopyMealForm.data:
        search_str = copy_form.search.data
        return redirect(url_for('public.compose_copy', searched=search_str, item_id=item_id))

    search_form = SearchForm()
    if search_form.validate_on_submit() and search_form.submitSearchForm.data:
        search_str = search_form.search.data
        return redirect(url_for('public.compose_search', searched=search_str, item_id=item.id))

    edit_form = EditForm()
    if edit_form.validate_on_submit():
        request_list = list(request.form)
        request_list.remove('qty')
        request_list.remove('csrf_token')
        index = request_list[0]

        assoc = db.session.query(ItemProductAssoc).get(index)
        old_qty = assoc.qty
        assoc.qty = edit_form.qty.data

        # total = {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0, 'qty': 0}
        # for a in item.products:
        #     total['qty'] += a.qty
        #     total['calories'] += a.qty * a.product.calories
        #     total['protein'] += a.qty * a.product.protein
        #     total['carbs'] += a.qty * a.product.carb
        #     total['fat'] += a.qty * a.product.fat
        #
        # item.carb = total['carbs'] / total['qty']
        # item.calories = total['calories'] / total['qty']
        # item.protein = total['protein'] / total['qty']
        # item.fat = total['fat'] / total['qty']

        delta = assoc.qty - old_qty
        old_item_qty = item.qty
        item.qty = item.qty + delta
        item.carb = (item.carb * old_item_qty + delta * assoc.product.carb) / item.qty
        item.calories = (item.calories * old_item_qty + delta * assoc.product.calories) / item.qty
        item.protein = (item.protein * old_item_qty + delta * assoc.product.protein) / item.qty
        item.fat = (item.fat * old_item_qty + delta * assoc.product.fat) / item.qty

        db.session.commit()
        return redirect(url_for('public.compose_meal', item_id=item_id))

    delete_form = DeleteForm()
    if delete_form.validate_on_submit() and delete_form.submitDeleteForm.data:
        while item.products:
            assoc = item.products.pop()
            db.session.delete(assoc)
        item.calories = 0
        item.carb = 0
        item.protein = 0
        item.fat = 0
        item.qty = 0
        db.session.commit()
        return redirect(url_for('public.compose_meal', item_id=item_id))

    save_form = SaveForm()
    if save_form.validate_on_submit() and save_form.submitSaveForm.data:
        item.saved = True
        db.session.commit()
        return redirect(url_for('public.add_meal'))

    return render_template('public/compose_meal.html', edit_form=edit_form, copy_form=copy_form, save_form=save_form,
                           delete_form=delete_form, user=current_user, item=item, total=total, search_form=search_form)


@blueprint.route("/compose_meal/<item_id>/<searched>", methods=['GET', 'POST'])
@login_required
def compose_search(item_id, searched) -> str or Response:
    """Renders search result for adding products to composed meals."""
    products = Product.query.filter(Product.name.contains(searched))
    print(products.all())
    form = QtyForm()
    if request.method == 'POST':
        item = Item.query.filter_by(id=item_id).first()
        request_list = list(request.form)
        request_list.remove('qty')
        request_list.remove('csrf_token')
        product_id = request_list[0]
        qty = form.qty.data
        product = Product.query.filter_by(id=product_id).first()

        assoc = ItemProductAssoc(qty=qty)
        assoc.product = product
        item.products.append(assoc)

        # total = {'calories': 0, 'protein': 0, 'carbs': 0, 'fat': 0, 'qty': 0}
        # for a in item.products:
        #     total['qty'] += a.qty
        #     total['calories'] += a.qty * a.product.calories
        #     total['protein'] += a.qty * a.product.protein
        #     total['carbs'] += a.qty * a.product.carb
        #     total['fat'] += a.qty * a.product.fat
        #
        # item.carb = total['carbs'] / total['qty']
        # item.calories = total['calories'] / total['qty']
        # item.protein = total['protein'] / total['qty']
        # item.fat = total['fat'] / total['qty']

        old_item_qty = item.qty
        item.qty += qty
        item.carb = (item.carb * old_item_qty + product.carb * qty) / item.qty
        item.protein = (item.protein * old_item_qty + product.protein * qty) / item.qty
        item.fat = (item.fat * old_item_qty + product.fat * qty) / item.qty
        item.calories = (item.calories * old_item_qty + product.calories * qty) / item.qty

        db.session.commit()
        return redirect(url_for('public.compose_meal', item_id=item_id))
    return render_template('public/compose_search.html',
                           user=current_user, products=products, searched=searched, form=form)


@blueprint.route("/compose_meal/<item_id>/copy/<searched>", methods=['GET', 'POST'])
@login_required
def compose_copy(item_id, searched) -> str or Response:
    """Renders search results for copying existing meals."""
    items = Item.query.filter(Item.name.contains(searched), Item.saved == True)
    if request.method == 'POST':
        request_list = list(request.form)
        copy_item_id = request_list[0]
        copy_item = db.session.query(Item).get(copy_item_id)
        item = db.session.query(Item).get(item_id)

        while item.products:
            a = item.products.pop()
            db.session.delete(a)

        for a in copy_item.products:
            new_a = ItemProductAssoc()
            new_a.product = a.product
            new_a.qty = a.qty
            item.products.append(new_a)

        item.carb = copy_item.carb
        item.calories = copy_item.calories
        item.protein = copy_item.protein
        item.fat = copy_item.fat
        item.qty = copy_item.qty
        db.session.commit()

        return redirect(url_for('public.compose_meal', item_id=item_id))

    return render_template('public/compose_copy.html', user=current_user, items=items, searched=searched)


@blueprint.route('/compose_meal/delete_pos')
@login_required
def delete_product_in_meal() -> Response:
    """Deletes the position from the meal"""
    index = request.args.get('index')
    item_id = request.args.get('item_id')
    item = db.session.query(Item).get(item_id)
    assoc = db.session.query(ItemProductAssoc).get(index)

    delta = -assoc.qty
    old_item_qty = item.qty
    item.qty = item.qty + delta
    if item.qty == 0:
        item.carb = 0
        item.calories = 0
        item.fat = 0
        item.protein = 0
    else:
        item.carb = (item.carb * old_item_qty + delta * assoc.product.carb) / item.qty
        item.calories = (item.calories * old_item_qty + delta * assoc.product.calories) / item.qty
        item.protein = (item.protein * old_item_qty + delta * assoc.product.protein) / item.qty
        item.fat = (item.fat * old_item_qty + delta * assoc.product.fat) / item.qty

    item.products.remove(assoc)
    db.session.delete(assoc)
    db.session.commit()
    return redirect(url_for('public.compose_meal', item_id=item_id))
