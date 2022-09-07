import datetime as dt
from mealswap.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship
from sqlalchemy.schema import Table


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
        return f"<User({self.email})>"


diet_item_table = Table(
    "diet_item",
    db.Model.metadata,
    db.Column("day_diet_id", db.ForeignKey('day_diet.id')),
    db.Column("item_id", db.ForeignKey('item.id'))
)


class DayDiet(db.Model):
    __tablename__ = 'day_diet'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = relationship('User', back_populates='diets')
    date = db.Column(db.Date, nullable=False)
    items = relationship("Item", secondary=diet_item_table)

    def __init__(self, user_id, user, date):
        self.user_id = user_id
        self.user = user
        self.date = date


item_product_table = Table(
    "item_product",
    db.Model.metadata,
    db.Column("item_id", db.ForeignKey('item.id')),
    db.Column("product_id", db.ForeignKey('product.id'))
)


class Item(db.Model):
    __tablename__ = 'item'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    protein = db.Column(db.Float, nullable=False)
    carb = db.Column(db.Float, nullable=False)
    fat = db.Column(db.Float, nullable=False)
    calories = db.Column(db.Float, nullable=False)
    link = db.Column(db.String(250))
    recipe = db.Column(db.Text)
    products = relationship("Product", secondary=item_product_table)

    def __init__(self, name, protein, carb, fat, calories=None, link=None, recipe=None):
        self.name = name
        self.protein = protein
        self.carb = carb
        self.fat = fat
        if calories:
            self.calories = calories
        else:
            self.calories = protein*4 + carb*4 + fat*9
        if link:
            self.link = link
        if recipe:
            self.recipe = recipe


class Product(db.Model):
    __tablename__ = 'product'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    protein = db.Column(db.Float, nullable=False)
    carb = db.Column(db.Float, nullable=False)
    fat = db.Column(db.Float, nullable=False)
    calories = db.Column(db.Float, nullable=False)

    def __init__(self, name, protein, carb, fat, calories=None):
        self.name = name
        self.protein = protein
        self.carb = carb
        self.fat = fat
        if calories:
            self.calories = calories
        else:
            self.calories = protein*4 + carb*4 + fat*9
