import datetime as dt
from mealswap.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship


class User(UserMixin, db.Model):
    """A class used to represent users of the app

    User class has relationships with:
    - DayDiet class - one-to-many
    - Item class - one-to-many
    - Settings class - one-to-one
    - RatingsAssoc - association
    """
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(250), nullable=False, unique=True)
    password = db.Column(db.String(250), nullable=False)
    name = db.Column(db.String(250), nullable=False)
    admin = db.Column(db.Boolean, nullable=False, default=False)
    registered_on = db.Column(db.DateTime, nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False, default=False)
    confirmed_on = db.Column(db.DateTime, nullable=True)
    diets = relationship('DayDiet', back_populates='user')
    items = relationship('Item', back_populates='user')
    settings = relationship('Settings', back_populates='user')
    ratings = relationship('RatingsAssoc')

    def __init__(self, email: str, password: str, name: str, confirmed: bool, admin: bool = False,
                 confirmed_on: dt.date = None):
        """
        :param email: user email address
        :param password: hashed user password
        :param name: username
        :param confirmed: True if user is verified, False if not
        :param admin: True if user is admin, False if not
        :param confirmed_on: date of user confirmation if verified
        """
        self.email = email
        self.password = password
        self.name = name
        self.admin = admin
        self.registered_on = dt.datetime.now()
        self.confirmed = confirmed
        self.confirmed_on = confirmed_on
        self.settings.append(Settings())

    def set_password(self, value: str):
        """Set password

        :param value: user input
        """
        self.password = generate_password_hash(value)

    def check_password(self, value: str):
        """Checks password hash

        :param value: user input
        """
        return check_password_hash(self.password, value)

    def delete_account(self):
        """Terminates account"""
        self.confirmed = False

    def __repr__(self):
        """User class representation as a string"""
        return f"<User({self.name})#{self.id}>"


class Settings(db.Model):
    """A class used to represent user settings (one-to-one relationship)

    Settings include macronutrient goals (parameters protein_goal, carb_goal, fat_goal, calories_goal) and locale
    (not implemented)
    """
    __tablename__ = 'settings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = relationship('User', back_populates='settings')
    protein_goal = db.Column(db.Float)
    carb_goal = db.Column(db.Float)
    fat_goal = db.Column(db.Float)
    calories_goal = db.Column(db.Float)
    locale = db.Column(db.String(250))


class RatingsAssoc(db.Model):
    """Association table to represent item ratings by users."""
    __tablename__ = 'ratings_assoc'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('user.id'))
    item_id = db.Column(db.ForeignKey('item.id'))
    rating = db.Column(db.Integer, nullable=False)
    item = relationship("Item")


class DietItemAssoc(db.Model):
    """Association table to represent items contained in particular diet days."""
    __tablename__ = "diet_item_assoc"

    id = db.Column(db.Integer, index=True, primary_key=True, autoincrement=True)
    diet_id = db.Column(db.ForeignKey('day_diet.id'))
    item_id = db.Column(db.ForeignKey('item.id'))
    qty = db.Column(db.Float, nullable=False)
    item = relationship("Item")


class DayDiet(db.Model):
    """A class used to represent diet days.

    Class has relationships with:
    - Item class - many-to-many
    - User class - many-to-one
    """
    __tablename__ = 'day_diet'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = relationship('User', back_populates='diets')
    date = db.Column(db.Date, nullable=False)
    weight = db.Column(db.Float)  # not implemented, weight of the user
    items = relationship("DietItemAssoc")

    def __init__(self, user: User, date: dt.date):
        """
        :param user: owner of the diet day
        :param date: date of the diet
        """
        self.user_id = user.id
        self.user = user
        self.date = date


class ItemProductAssoc(db.Model):
    """Association table to join items and products"""
    __tablename__ = "item_product_assoc"

    id = db.Column(db.Integer, index=True, primary_key=True)
    item_id = db.Column(db.ForeignKey('item.id'))
    product_id = db.Column(db.ForeignKey('product.id'))
    qty = db.Column(db.Float, nullable=False)
    product = relationship("Product")


class Item(db.Model):
    """A class that represents item - food that can be added to diet.

    Class has relationships with:
    - User: many-to-one
    - DayDiet: many-to-many
    - Product: many-to-many
    - RatingsAssoc: association
    """
    __tablename__ = 'item'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    protein = db.Column(db.Float, nullable=False)
    carb = db.Column(db.Float, nullable=False)
    fat = db.Column(db.Float, nullable=False)
    calories = db.Column(db.Float, nullable=False)
    has_weight = db.Column(db.Boolean, nullable=False)
    servings = db.Column(db.Integer)
    qty = db.Column(db.Float)
    link = db.Column(db.String(250))
    recipe = db.Column(db.Text)
    saved = db.Column(db.Boolean)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = relationship('User', back_populates='items')
    products = relationship("ItemProductAssoc")

    def __init__(self, name: str, protein: float, carb: float, fat: float, user: User, has_weight: bool, qty: float,
                 servings: int, calories: float = None, link: str = None, recipe: str = None, saved: bool = None):
        """
        :param name: name of the item
        :param protein: protein amount per 100g or ea of food
        :param carb: carbohydrate amount per 100g or ea of food
        :param fat: fat amount per 100g or ea of food
        :param user: user adding the item
        :param has_weight: weighted meal flag; if True, the macronutrient values are amounts per 100g, otherwise they
        are amounts per ea
        :param qty: total weight of the meal
        :param servings: number of servings that can be made of the total weight
        :param calories: number of calories. Default None means that calories are calculated from macronutrient values
        :param link: link to the recipe and/or item details
        :param recipe: recipe text
        :param saved: if True, the meal cannot be edited but can be added to diet; if False, the meal can be edited,
        but has to be saved before adding to diet
        """
        self.name = name
        self.protein = protein
        self.carb = carb
        self.fat = fat
        self.user_id = user.id
        self.user = user
        self.has_weight = has_weight
        self.qty = qty
        self.servings = servings
        if calories:
            self.calories = calories
        else:
            self.calories = protein*4 + carb*4 + fat*9
        if link:
            self.link = link
        if recipe:
            self.recipe = recipe
        if saved:
            self.saved = True
        else:
            self.saved = False


class Product(db.Model):
    """A class that represents products that are building blocks of meals.

    Class has relationships with:
    - Item: many-to-many
    """
    __tablename__ = 'product'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    protein = db.Column(db.Float, nullable=False)
    carb = db.Column(db.Float, nullable=False)
    fat = db.Column(db.Float, nullable=False)
    calories = db.Column(db.Float, nullable=False)
    weight_per_ea = db.Column(db.Float)

    def __init__(self, name: str, protein: float, carb: float, fat: float, weight_per_ea: float,
                 calories: float = None):
        """
        :param name: name of the product
        :param protein: amount of protein per 100g
        :param carb: amount of carbohydrates per 100g
        :param fat: amount of fat per 100g
        :param weight_per_ea: how much 1 ea of products weighs (optional)
        :param calories: amount of calories per 100g. Default None means that calories are calculated from
        macronutrient values
        """
        self.name = name
        self.protein = protein
        self.carb = carb
        self.fat = fat
        if calories:
            self.calories = calories
        else:
            self.calories = protein*4 + carb*4 + fat*9
        self.weight_per_ea = weight_per_ea
