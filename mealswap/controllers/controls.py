from flask_sqlalchemy import Pagination

from mealswap.models.models import *
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


# dictionary that joins Enum with actual models
dictionary = {0: User,
              1: Settings,
              2: RatingsAssoc,
              3: DietItemAssoc,
              4: DayDiet,
              5: ItemProductAssoc,
              6: Item,
              7: Product}


def get_element_by_id(model: Model, element_id: str or int) -> db.Model or None:
    """
    Searches the table in database and finds object by id.

    :param model: table in the database to be searched
    :param element_id: id of the object to be returned
    :return: database object if found else None
    """
    return dictionary[model.value].query.filter_by(id=int(element_id)).first()


def get_element_list_by_ids(model: Model, element_ids: list, paginate=False, **kwargs) -> list or Pagination:
    """
    Searches the table in database and finds objects by their ids.

    :param model: table in the database to be searched
    :param element_ids: list of ids of items to be returned
    :param paginate: boolean for paginating the results. Default is False.
    :return: list of database objects
    """
    if paginate:
        page = kwargs.get('page', 1)
        per_page = kwargs.get('per_page', 5)
        return db.session.query(dictionary[model.value])\
            .filter(dictionary[model.value].id.in_(element_ids)).paginate(page=page, per_page=per_page)
    return db.session.query(dictionary[model.value]).filter(dictionary[model.value].id.in_(element_ids)).all()


def get_all_elements(model: Model) -> list:
    """
    Returns all objects in a chosen table.

    :param model: table in the database
    :return: list of database objects
    """
    return dictionary[model.value].query.all()


def get_user_by_email(email: str) -> User or None:
    """
    Returns User object that has provided email.

    :param email: email of the user to be returned
    :return: User if found else None
    """
    return User.query.filter_by(email=email).first()


def get_diet_by_date(date: str) -> DayDiet or None:
    """
    Returns DayDiet object by date.

    :param date: date of the diet to be returned
    :return: DayDiet if found else None
    """
    return DayDiet.query.filter_by(date=date).first()


def get_diets_in_current_month() -> list:
    """
    Returns list of the DayDiet objects in current month.

    :return: list of DayDiet objects
    """
    today = dt.date.today()
    first_day = dt.date(today.year, today.month, 1)
    last_day = dt.date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
    return DayDiet.query.filter(DayDiet.date.between(first_day, last_day)).all()


def get_saved_items(paginate=False, **kwargs) -> list:
    """
    Returns list of saved Item objects.

    :param paginate: boolean for paginating the results. Default is False.
    :return: list of saved Item objects
    """
    if paginate:
        page = kwargs.get('page', 1)
        per_page = kwargs.get('per_page', 5)
        return Item.query.filter_by(saved=True).paginate(page=page, per_page=per_page)
    return Item.query.filter_by(saved=True).all()


def get_open_items_by_user(user: User) -> list:
    """
    Returns open Items that have been created by provided User.

    :param user: the User object that is creator of searched meals
    :return: list of editable (not saved) Item objects
    """
    return Item.query.filter_by(saved=False, user_id=user.id).all()


def get_saved_items_by_name(name: str, paginate=False, **kwargs) -> list:
    """
    Searches for Items by comparing their name to provided string.

    :param name: string for name search query
    :param paginate: boolean for paginating the results. Default is False.
    :return: list of Item objects
    """
    if paginate:
        page = kwargs['page']
        per_page = kwargs['per_page']
        return Item.query.filter(Item.name.contains(name), Item.saved == True).paginate(page=page, per_page=per_page)
    return Item.query.filter(Item.name.contains(name), Item.saved == True).all()


def get_saved_composed_items_by_name(name: str, pagination=False, **kwargs) -> list:
    """
    Searches for saved composed Items that can be copied.

    :param name: string for name search query
    :param pagination: boolean for paginating the results. Default is False.
    :return: list of Item objects
    """
    if pagination:
        page = kwargs['page']
        per_page = kwargs['per_page']
        return Item.query.filter(Item.name.contains(name), Item.saved == True, Item.has_weight == True,
                                 Item.products is not None, Item.servings > 0).paginate(page=page, per_page=per_page)
    return Item.query.filter(Item.name.contains(name), Item.saved == True, Item.has_weight == True,
                             Item.products is not None, Item.servings > 0).all()


def get_products_by_name(name: str, paginate=False, **kwargs) -> list:
    """
    Searches for Products by name.

    :param name: string for name search query
    :param paginate: boolean for paginating the results. Default is False.
    :return: list of Product objects
    """
    if paginate:
        page = kwargs.get('page', 1)
        per_page = kwargs.get('per_page', 5)
        Product.query.filter(Product.name.contains(name)).paginate(page=page, per_page=per_page)
    return Product.query.filter(Product.name.contains(name)).all()


def get_ratings_by_user(user: User) -> list:
    """
    Searches for Ratings by User.

    :param user: User object that has ratings to be returned
    :return: list of RatingsAssoc objects
    """
    return RatingsAssoc.query.filter_by(user_id=user.id).all()


def get_ratings_count_by_user(user: User) -> int:
    """
    Returns ratings count.

    :param user: User object that has rated Items
    :return: ratings count by user
    """
    return RatingsAssoc.query.filter_by(user_id=user.id).count()


def get_rating_by_ids(item_id: int, user_id: int) -> RatingsAssoc or None:
    """
    Searches for rating of an Item by User

    :param item_id: id of the Item
    :param user_id: id of the User
    """
    return RatingsAssoc.query.filter_by(item_id=item_id, user_id=user_id).first()


def get_settings_by_user(user: User) -> Settings:
    """
    Returns Settings connected to a User.

    :param user: User object that has Settings
    :return: Settings object
    """
    return user.settings[0]


def set_rating(item: Item, user: User, rating: str) -> db.Model:
    """
    Sets rating for Item by User by adding RatingsAssoc object to database

    :param item: Item that the rating will be set
    :param user: User that sets the rating
    :param rating: the rating of Item by User
    """
    assoc = get_rating_by_ids(item.id, user.id)
    if assoc:
        assoc.rating = int(rating)
    else:
        assoc = RatingsAssoc(rating=int(rating))
        assoc.item = item
        user.ratings.append(assoc)
    db.session.commit()

    return assoc


def add_product_to_db(name: str, protein: float, carb: float, fat: float, user: User, weight_per_ea: float) -> Product:
    """
    Adds Product to database that can be used to compose meals.

    Also creates a corresponding Item object that can be used to add to diet.

    :param name: name of the product
    :param protein: protein amount per 100g of the product
    :param carb: carbohydrate amount per 100g of the product
    :param fat: fat amount per 100g of the product
    :param user: User that adds the product to the database
    :param weight_per_ea: optional value, weight per ea to allow adding ea of products in the diet/meals
    :return: created Product object
    """
    product = Product(
        name=name,
        protein=protein,
        carb=carb,
        fat=fat,
        weight_per_ea=weight_per_ea
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
    # if weight per ea is defined, set servings to 1 so that a proper form can be rendered that can handle ea
    if weight_per_ea:
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

    return product


def add_meal_to_db(name: str, protein: float, carb: float, fat: float, user: User, has_weight: bool, link: str,
                   recipe: str, saved: bool, qty: float, servings: int) -> db.Model:
    """
    Adds a meal to database.

    To add a weighted meal (i.e. known data for values of macronutrients per 100g), set has_weight = True, saved = True.
    To add a composite meal, set has_weight = True, qty = 0, saved = False (enables editing).
    To add a meal with macronutrient data per serving, set has_weight = False, saved = True.

    :param name: name of the meal
    :param protein: protein amount per 100g or ea of the product (depending on has_weight)
    :param carb: carb amount per 100g or ea of the product (depending on has_weight)
    :param fat: fat amount per 100g or ea of the product (depending on has_weight)
    :param user: User adding the product to the database
    :param has_weight: True if macronutrient data is defined per 100g, False if only per ea
    :param link: link to the meal recipe/page (nullable)
    :param recipe: text recipe of the meal (nullable)
    :param saved: True if meal is saved and can be added to diet, False if it can be edited, but not added to diet
    :param qty: total weight of the meal in grams, 0 for composite meals
    :param servings: number of servings that can be made out of defined qty
    :return: created Item object
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


def set_meal_recipe(item: Item, link: str, recipe: str, servings: int):
    """
    Updates additional meal data: link, recipe, servings

    :param item: Item that is edited
    :param link: link to the meal recipe/page (nullable)
    :param recipe: text recipe of the meal (nullable)
    :param servings: number of servings that can be made out of defined qty
    :return: None
    """
    item.link = link
    item.recipe = recipe
    item.servings = servings
    db.session.commit()

    return None


def set_qty_in_meal(assoc: ItemProductAssoc, item: Item, new_qty: float) -> None:
    """
    Updates quantity for Product in Item.

    :param assoc: ItemProductAssoc that connects Product to the Item
    :param item: Item that has its quantity edited
    :param new_qty: new quantity defined by editing user
    :return: None
    """
    old_qty = assoc.qty
    assoc.qty = new_qty

    delta = assoc.qty - old_qty
    old_item_qty = item.qty
    item.qty = item.qty + delta

    # defining new macronutrient values per 100g
    item.carb = (item.carb * old_item_qty + delta * assoc.product.carb) / item.qty
    item.calories = (item.calories * old_item_qty + delta * assoc.product.calories) / item.qty
    item.protein = (item.protein * old_item_qty + delta * assoc.product.protein) / item.qty
    item.fat = (item.fat * old_item_qty + delta * assoc.product.fat) / item.qty

    db.session.commit()

    return None


def clear_meal(item: Item) -> None:
    """
    Deletes all ItemProductsAssocs in Item and changes macronutrient values to 0.

    :param item: Item that has its data cleared
    :return: None
    """
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


def delete_meal_from_db(item: Item) -> None:
    """
    Deletes Item from database.

    :param item: Item to be deleted
    :return: None
    """
    clear_meal(item)
    db.session.delete(item)
    db.session.commit()

    return None


def save_meal(item: Item) -> None:
    """
    Changes 'saved' value of Item to True, enabling adding to diet but disabling editing the meal.

    :param item: Item that has its 'saved' value changed
    :return: None
    """
    item.saved = True
    db.session.commit()

    return None


def add_product_to_meal(item: Item, product: Product, qty: float) -> None:
    """
    Adds a Product to Item.

    :param item: Item that is edited
    :param product: Product that is added to Item
    :param qty: weight of the added Product
    :return: None
    """
    assoc = ItemProductAssoc(qty=qty)
    assoc.product = product
    item.products.append(assoc)

    old_item_qty = item.qty
    item.qty += qty
    # defining new macronutrient values per 100g
    item.carb = (item.carb * old_item_qty + product.carb * qty) / item.qty
    item.protein = (item.protein * old_item_qty + product.protein * qty) / item.qty
    item.fat = (item.fat * old_item_qty + product.fat * qty) / item.qty
    item.calories = (item.calories * old_item_qty + product.calories * qty) / item.qty

    db.session.commit()

    return None


def copy_meal(item: Item, copy_item: Item) -> None:
    """
    Substitutes current data for item with a different item.

    :param item: Item that is edited
    :param copy_item: Item that is copied
    :return: None
    """
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


def delete_index_from_meal(item: Item, assoc: ItemProductAssoc) -> None:
    """
    Deletes an ItemProductAssoc in Item.

    :param item: Item that is edited
    :param assoc: ItemProductAssoc that is deleted
    :return: None
    """
    delta = -assoc.qty
    old_item_qty = item.qty
    item.qty = item.qty + delta
    # defining new macronutrient values per 100g
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


def add_diet(user: User, date: dt.date or str) -> DayDiet:
    """
    Creates a new DayDiet in database.

    :param user: User that creates the DayDiet object
    :param date: date of the created DayDiet object
    :return: DayDiet object
    """
    if type(date) == str:
        date = dt.datetime.strptime(date, "%Y-%m-%d").date()
    diet = DayDiet(user=user, date=date)
    db.session.add(diet)
    db.session.commit()

    return diet


def copy_diet(diet: DayDiet, copied: DayDiet) -> None:
    """
    Copies a DayDiet data from another date.

    :param diet: DayDiet that is edited
    :param copied: DayDiet that is copied
    :return:
    """
    for a in copied.items:
        new_a = DietItemAssoc(qty=a.qty)
        new_a.item = a.item
        diet.items.append(new_a)
    db.session.commit()

    return None


def delete_diet(diet: DayDiet) -> None:
    """
    Deletes DayDiet from database.

    :param diet: DayDiet to be deleted
    :return: None
    """
    if diet:
        while diet.items:
            assoc = diet.items.pop()
            db.session.delete(assoc)
        db.session.delete(diet)
        db.session.commit()

    return None


def edit_item_qty_in_diet(assoc: DietItemAssoc, new_qty: float) -> None:
    """
    Edits quantity for Item in Diet.

    :param assoc: DietItemAssoc that connects Item to DayDiet
    :param new_qty: new quantity for the Item
    :return: None
    """
    assoc.qty = new_qty
    db.session.commit()

    return None


def delete_item_from_diet(assoc: DietItemAssoc, diet: DayDiet) -> None:
    """
    Deletes Item from Diet.

    :param assoc: DietItemAssoc that connects Item to DayDiet
    :param diet: DayDiet that has Item removed
    :return: None
    """
    diet.items.remove(assoc)
    db.session.delete(assoc)
    db.session.commit()

    return None


def add_item_to_diet(item: Item, qty: float, ea: int, diet: DayDiet) -> None:
    """
    Adds Item to Diet.

    If Item has defined macronutrient values per 100g and number of servings, quantity can be added both by weight and
    by ea.
    If Item has only defined macronutrient values per 100g, it can be added by weight.
    If Item has only defined macronutrient values per ea, it can be added by ea.

    :param item: Item to be added
    :param qty: quantity of the added Item
    :param ea: number of ea of the Item
    :param diet: DayDiet that has Item added
    :return: None
    """
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


def add_user(email: str, password: str, name: str) -> None:
    """
    Adds User to database.

    :param email: new user's email address
    :param password: new user's password
    :param name: new user's name
    :return: None
    """
    password = generate_password_hash(password)
    new_user = User(email, password, name, confirmed=False)
    db.session.add(new_user)
    db.session.commit()

    return None


def set_password(user: User, password: str) -> None:
    """
    Changes User password.

    :param user: user that has their password changed
    :param password: new password
    :return: None
    """
    user.set_password(password)
    db.session.commit()

    return None


def delete_account(user: User) -> None:
    """
    Terminates user's account.

    :param user: User that is terminated
    :return: None
    """
    user.delete_account()
    db.session.commit()

    return None


def set_diet_goals(user: User, calories: float, protein: float or int, carb: float or int, fat: float or int,
                   percentage: bool):
    """
    Changes diet goals for the User in their Settings.

    Users can define their macronutrient goals either as percentages of total caloric intake (when percentage = True)
    or they can provide exact values of macronutrients in grams.

    :param user: User that has its diet goals set
    :param calories: caloric goal in kcal
    :param protein: protein intake goal, float if in grams, int if in percentage
    :param carb: carbohydrate intake goal, float if in grams, int if in percentage
    :param fat: fat intake goal, float if in grams, int if in percentage
    :param percentage: True if macronutrient data is in percentages, False if in grams
    :return:
    """
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


def update_weight(diet: DayDiet, weight: float) -> None:
    """
    Updates User weight for a given DayDiet.
    :param diet: DayDiet that contains data for a given date
    :param weight: weight of the body as measured by the User
    :return: None
    """
    diet.weight = weight
    db.session.commit()

    return None
