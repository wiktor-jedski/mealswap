from mealswap.models import *
from mealswap.extensions import db
from enum import Enum
import datetime as dt
from werkzeug.security import generate_password_hash
import calendar


# model class
class Model(Enum):
    USER = 0
    SETTINGS = 1
    RATINGS = 2
    DIET_ITEM = 3
    DAY = 4
    ITEM_PRODUCT = 5
    ITEM = 6
    PRODUCT = 7


dictionary = {0: User,
              1: Settings,
              2: RatingsAssoc,
              3: DietItemAssoc,
              4: DayDiet,
              5: ItemProductAssoc,
              6: Item,
              7: Product}


def get_element_by_id(model, element_id) -> db.Model:
    return dictionary[model.value].query.filter_by(id=int(element_id)).first()


def get_element_list_by_ids(model, element_ids) -> list:
    return db.session.query(dictionary[model.value]).filter(dictionary[model.value].id.in_(element_ids)).all()


def get_all_elements(model) -> list:
    return dictionary[model.value].query.all()


def get_user_by_email(email) -> User:
    return User.query.filter_by(email=email).first()


def get_diet_by_date(date) -> DayDiet:
    return DayDiet.query.filter_by(date=date).first()


def get_diets_in_current_month() -> list:
    today = dt.date.today()
    first_day = dt.date(today.year, today.month, 1)
    last_day = dt.date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
    return DayDiet.query.filter(DayDiet.date.between(first_day, last_day)).all()


def get_saved_items() -> list:
    return Item.query.filter_by(saved=True).all()


def get_open_items_by_user(user) -> list:
    return Item.query.filter_by(saved=False, user_id=user.id).all()


def get_saved_items_by_name(name) -> list:
    return Item.query.filter(Item.name.contains(name), Item.saved == True).all()


def get_saved_composed_items_by_name(name) -> list:
    return Item.query.filter(Item.name.contains(name), Item.saved == True,
                             Item.products is not None, Item.servings > 0).all()


def get_products_by_name(name) -> list:
    return Product.query.filter(Product.name.contains(name)).all()


def get_ratings_by_user(user) -> list:
    return RatingsAssoc.query.filter_by(user_id=user.id).all()


def get_ratings_count_by_user(user) -> int:
    return RatingsAssoc.query.filter_by(user_id=user.id).count()


def get_rating_by_ids(item_id, user_id) -> RatingsAssoc:
    return RatingsAssoc.query.filter_by(item_id=item_id, user_id=user_id).first()


def set_rating(item, user, rating) -> str:
    assoc = get_rating_by_ids(item.id, user.id)
    if assoc:
        assoc.rating = int(rating)
    else:
        assoc = RatingsAssoc(rating=int(rating))
        assoc.item = item
        user.ratings.append(assoc)
    db.session.commit()

    return assoc.item.name


def add_product_to_db(name, protein, carb, fat, user, weight_per_ea=None):
    product = Product(
        name=name,
        protein=protein,
        carb=carb,
        fat=fat
    )
    item = Item(
        name=name,
        protein=protein,
        carb=carb,
        fat=fat,
        has_weight=True,
        user=user,
        saved=True,
        qty=0,
        servings=0
    )
    if weight_per_ea:
        product.weight_per_ea = weight_per_ea
        item.qty = weight_per_ea
        item.servings = 1
    else:
        item.servings = 0
    db.session.add(product)
    assoc = ItemProductAssoc(qty=100)
    assoc.product = product
    item.products.append(assoc)
    db.session.add(item)
    db.session.commit()

    return name


def add_meal_to_db(name, protein, carb, fat, user, has_weight, link, recipe, saved, qty, servings):
    """Adds a meal to database.
    To add a weighted meal (i.e. known data for values of macronutrients per 100g), set has_weight = True.
    To add a composite meal, set has_weight = True, qty = 0, saved = False (enables editing).
    To add a meal with macronutrient data per serving, set has_weight = False.
    """
    item = Item(
        name=name,
        protein=protein,
        carb=carb,
        fat=fat,
        user=user,
        has_weight=has_weight,
        link=link,
        recipe=recipe,
        saved=saved,
        qty=qty,
        servings=servings
    )

    db.session.add(item)
    db.session.commit()

    return item


def set_meal_recipe(item, link, recipe, servings):
    item.link = link
    item.recipe = recipe
    item.servings = servings
    db.session.commit()

    return None


def set_qty_in_meal(assoc, item, new_qty):
    old_qty = assoc.qty
    assoc.qty = new_qty

    delta = assoc.qty - old_qty
    old_item_qty = item.qty
    item.qty = item.qty + delta
    item.carb = (item.carb * old_item_qty + delta * assoc.product.carb) / item.qty
    item.calories = (item.calories * old_item_qty + delta * assoc.product.calories) / item.qty
    item.protein = (item.protein * old_item_qty + delta * assoc.product.protein) / item.qty
    item.fat = (item.fat * old_item_qty + delta * assoc.product.fat) / item.qty

    db.session.commit()

    return None


def clear_meal(item):
    while item.products:
        assoc = item.products.pop()
        db.session.delete(assoc)
    item.calories = 0
    item.carb = 0
    item.protein = 0
    item.fat = 0
    item.qty = 0
    db.session.commit()

    return None


def delete_meal_from_db(item):
    clear_meal(item)
    db.session.delete(item)
    db.session.commit()

    return None


def save_meal(item):
    item.saved = True
    db.session.commit()

    return None


def add_product_to_meal(item, product, qty):
    assoc = ItemProductAssoc(qty=qty)
    assoc.product = product
    item.products.append(assoc)

    old_item_qty = item.qty
    item.qty += qty
    item.carb = (item.carb * old_item_qty + product.carb * qty) / item.qty
    item.protein = (item.protein * old_item_qty + product.protein * qty) / item.qty
    item.fat = (item.fat * old_item_qty + product.fat * qty) / item.qty
    item.calories = (item.calories * old_item_qty + product.calories * qty) / item.qty

    db.session.commit()

    return None


def copy_meal(item, copy_item):
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
    item.servings = copy_item.servings
    item.recipe = copy_item.recipe
    item.link = copy_item.link
    db.session.commit()

    return None


def delete_index_from_meal(item, assoc):
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

    return None


def add_diet(user, date):
    date = dt.datetime.strptime(date, "%Y-%m-%d").date()
    diet = DayDiet(user=user, date=date)
    db.session.add(diet)
    db.session.commit()

    return diet


def copy_diet(copied, diet):
    for a in copied.items:
        new_a = DietItemAssoc(qty=a.qty)
        new_a.item = a.item
        diet.items.append(new_a)
    db.session.commit()

    return None


def delete_diet(diet):
    if diet:
        while diet.items:
            assoc = diet.items.pop()
            db.session.delete(assoc)
        db.session.delete(diet)
        db.session.commit()

    return None


def edit_item_qty_in_diet(assoc, new_qty):
    assoc.qty = new_qty
    db.session.commit()

    return None


def delete_item_in_diet(assoc, diet):
    diet.items.remove(assoc)
    db.session.delete(assoc)
    db.session.commit()

    return None


def add_item_to_diet(item, qty, ea, diet):
    if item.has_weight:
        if qty:
            assoc = DietItemAssoc(qty=qty)
        else:
            assoc = DietItemAssoc(qty=ea*item.qty/item.servings)
    else:
        assoc = DietItemAssoc(qty=ea)
    assoc.item = item
    diet.items.append(assoc)
    db.session.commit()

    return None


def add_user(email, password, name):
    password = generate_password_hash(password)
    new_user = User(email, password, name, confirmed=False)
    db.session.add(new_user)
    db.session.commit()

    return None


def set_password(user, password):
    user.set_password(password)
    db.session.commit()

    return None


def delete_account(user):
    user.delete_account()
    db.session.commit()

    return None


def set_diet_goals(user, calories, protein, carb, fat, percentage):
    settings = user.settings[0]
    if percentage:
        settings.calories_goal = calories
        settings.protein_goal = calories * protein / 100 / 4
        settings.carb_goal = calories * carb / 100 / 4
        settings.fat_goal = calories * fat / 100 / 9
    else:
        if calories:
            settings.calories_goal = calories
        if protein:
            settings.protein_goal = protein
        if carb:
            settings.carb_goal = carb
        if fat:
            settings.fat_goal = fat
    db.session.commit()

    return None
