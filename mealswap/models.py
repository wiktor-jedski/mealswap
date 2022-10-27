import datetime as dt
from mealswap.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship


class User(UserMixin, db.Model):
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

    def __init__(self, email, password, name, confirmed, admin=False, confirmed_on=None):
        self.email = email
        self.password = password
        self.name = name
        self.admin = admin
        self.registered_on = dt.datetime.now()
        self.confirmed = confirmed
        self.confirmed_on = confirmed_on

    def set_password(self, value):
        """Set password"""
        self.password = generate_password_hash(value)

    def check_password(self, value):
        """Checks password hash"""
        return check_password_hash(self.password, value)

    def __repr__(self):
        """User class representation as a string"""
        return f"<User({self.name})#{self.id}>"


class Settings(db.Model):
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
    __tablename__ = 'ratings_assoc'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('user.id'))
    item_id = db.Column(db.ForeignKey('item.id'))
    rating = db.Column(db.Integer, nullable=False)
    item = relationship("Item")


class DietItemAssoc(db.Model):
    __tablename__ = "diet_item_assoc"

    id = db.Column(db.Integer, index=True, primary_key=True, autoincrement=True)
    diet_id = db.Column(db.ForeignKey('day_diet.id'))
    item_id = db.Column(db.ForeignKey('item.id'))
    qty = db.Column(db.Float, nullable=False)
    item = relationship("Item")


class DayDiet(db.Model):
    __tablename__ = 'day_diet'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = relationship('User', back_populates='diets')
    date = db.Column(db.Date, nullable=False)
    weight = db.Column(db.Float)
    items = relationship("DietItemAssoc")

    def __init__(self, user, date):
        self.user_id = user.id
        self.user = user
        self.date = date


class ItemProductAssoc(db.Model):
    __tablename__ = "item_product_assoc"

    id = db.Column(db.Integer, index=True, primary_key=True)
    item_id = db.Column(db.ForeignKey('item.id'))
    product_id = db.Column(db.ForeignKey('product.id'))
    qty = db.Column(db.Float, nullable=False)
    product = relationship("Product")


class Item(db.Model):
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

    def __init__(self, name, protein, carb, fat, user, has_weight, qty, servings, calories=None, link=None, recipe=None,
                 saved=None):
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
    __tablename__ = 'product'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    protein = db.Column(db.Float, nullable=False)
    carb = db.Column(db.Float, nullable=False)
    fat = db.Column(db.Float, nullable=False)
    calories = db.Column(db.Float, nullable=False)
    weight_per_ea = db.Column(db.Float)

    def __init__(self, name, protein, carb, fat, calories=None):
        self.name = name
        self.protein = protein
        self.carb = carb
        self.fat = fat
        if calories:
            self.calories = calories
        else:
            self.calories = protein*4 + carb*4 + fat*9
        self.weight_per_ea = None
