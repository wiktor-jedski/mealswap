import datetime as dt
import calendar
from typing import List

from mealswap.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import relationship, declared_attr


# old models
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
        self.password = generate_password_hash(password)
        self.name = name
        self.admin = admin
        self.registered_on = dt.datetime.now()
        self.confirmed = confirmed
        self.confirmed_on = confirmed_on
        self.settings.append(Settings())

        db.session.add(self)
        db.session.commit()

    def set_password(self, value: str):
        """Set password

        :param value: user input
        """
        self.password = generate_password_hash(value)
        db.session.commit()

    def check_password(self, value: str):
        """Checks password hash

        :param value: user input
        """
        return check_password_hash(self.password, value)

    def delete_account(self):
        """Terminates account"""
        self.confirmed = False
        db.session.commit()

    def __repr__(self):
        """User class representation as a string"""
        return f"<User({self.name})#{self.id}>"


class Settings(db.Model):
    """A class used to represent user settings (one-to-one relationship)

    Settings include macronutrient goals (parameters protein_goal, carb_goal, fat_goal, calories_goal)
    """
    __tablename__ = 'settings'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = relationship('User', back_populates='settings')
    protein_goal = db.Column(db.Float)
    carb_goal = db.Column(db.Float)
    fat_goal = db.Column(db.Float)
    calories_goal = db.Column(db.Float)

    def set_percentage_diet_goals(self, calories: float, protein: int, carb: int, fat: int) -> None:
        """
        Changes diet goals for the User in Settings.
        Sets goals as percentages of total caloric intake.

        :param calories: caloric goal in kcal
        :param protein: protein goal as percentage
        :param carb: carb goal as percentage
        :param fat: fat goal as percentage
        :return: None
        """
        self.calories_goal = calories
        self.protein_goal = calories * protein / 100 / 4
        self.carb_goal = calories * carb / 100 / 4
        self.fat_goal = calories * fat / 100 / 9
        db.session.commit()

        return None

    def set_weighted_diet_goals(self, calories: float, protein: float, carb: float, fat: float) -> None:
        """
        Changes diet goals for the User in Settings.
        Sets goals as weight of macronutrients/number of calories.

        :param calories: caloric goal in kcal
        :param protein: protein goal in grams
        :param carb: carb goal in grams
        :param fat: fat goal in grams
        :return: None
        """
        if calories:
            self.calories_goal = calories
        if protein:
            self.protein_goal = protein
        if carb:
            self.carb_goal = carb
        if fat:
            self.fat_goal = fat
        db.session.commit()

        return None


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
    weight = db.Column(db.Float)
    items = relationship("DietItemAssoc")

    def __init__(self, user: User, date: dt.date):
        """
        :param user: owner of the diet day
        :param date: date of the diet
        """
        self.user_id = user.id
        self.user = user
        self.date = date

    @staticmethod
    def get_diets_in_current_month() -> List:
        """
        Returns list of the DayDiet objects in current month.

        :return: list of DayDiet objects
        """
        today = dt.date.today()
        first_day = dt.date(today.year, today.month, 1)
        last_day = dt.date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
        return DayDiet.query.filter(DayDiet.date.between(first_day, last_day)).all()


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


class ItemProductAssoc(db.Model):
    """Association table to join items and products"""
    __tablename__ = "item_product_assoc"

    id = db.Column(db.Integer, index=True, primary_key=True)
    item_id = db.Column(db.ForeignKey('item.id'))
    product_id = db.Column(db.ForeignKey('product.id'))
    qty = db.Column(db.Float, nullable=False)
    product = relationship("Product")


# NEW MODELS
class RatingAssoc(db.Model):
    """Association table to represent meal ratings by users."""
    __tablename__ = 'rating_assoc'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('user.id'))
    meal_id = db.Column(db.ForeignKey('meal.id'))
    rating = db.Column(db.Integer, nullable=False)
    meal = relationship("Meal")


class Meal(db.Model):
    """
    Represents meal that can be added to the diet.

    Class has relationships with:
    - User: many-to-one
    - DayDiet: many-to-many
    - RatingsAssoc: association
    """
    __tablename__ = 'meal'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), nullable=False)
    protein = db.Column(db.Float, nullable=False)
    carb = db.Column(db.Float, nullable=False)
    fat = db.Column(db.Float, nullable=False)
    calories = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    # user = relationship('User', back_populates='meals')
    saved = db.Column(db.Boolean)
    type = db.Column(db.String(20))

    __mapper_args__ = {
        "polymorphic_identity": "meal",
        "polymorphic_on": type,
    }

    def set_rating(self, user: User, rating: str) -> RatingAssoc:
        """
        Sets rating for Meal by User by adding RatingAssoc object to database.

        :param user: User that sets the rating
        :param rating: the rating of Meal by User
        :return: RatingAssoc object
        """
        assoc = RatingAssoc.query.filter_by(meal_id=self.id, user_id=user.id).first()
        if assoc:
            assoc.rating = int(rating)
        else:
            assoc = RatingAssoc(rating=int(rating))
            assoc.meal = self
            user.ratings.append(assoc)
        db.session.commit()

        return assoc


class CompositeProductAssoc(db.Model):
    """Association table to join meals and products"""
    __tablename__ = "composite_product_assoc"

    id = db.Column(db.Integer, index=True, primary_key=True)
    composite_id = db.Column(db.ForeignKey('composite_meal.id'))
    product_id = db.Column(db.ForeignKey('product_meal.id'))
    qty = db.Column(db.Float, nullable=False)
    product = relationship("ProductMeal")


class ProductMeal(Meal):
    """
    Represents products that can be added to the diet or used as building blocks for ComposedMeal.
    """
    __tablename__ = "product_meal"
    __mapper_args__ = {
        "polymorphic_identity": "product_meal"
    }
    id = db.Column(db.Integer, db.ForeignKey("meal.id"), primary_key=True)
    units = relationship("ProductMealUnit")

    def __init__(self, name: str, protein: float, carb: float, fat: float, user: User):
        """
        Creates a ProductMeal in the database.

        :param name: name of the product
        :param protein: protein content per 100g
        :param carb: carb content per 100g
        :param fat: fat content per 100g
        :param user: User that created the product
        """
        self.name = name
        self.protein = protein
        self.carb = carb
        self.fat = fat
        self.user = user
        self.saved = True
        self.units.append(ProductMealUnit(description="grams", weight=1))

        db.session.add(self)
        db.session.commit()


class CompositeMeal(Meal):
    """
    Represents meals that are composed of ProductMeals.
    """
    __tablename__ = "composite_meal"
    __mapper_args__ = {
        "polymorphic_identity": "composite_meal"
    }
    id = db.Column(db.Integer, db.ForeignKey("meal.id"), primary_key=True)
    qty = db.Column(db.Float)
    link = db.Column(db.String(250))
    recipe = db.Column(db.Text)
    products = relationship("CompositeProductAssoc")
    units = relationship("CompositeMealUnit")

    def __init__(self, name: str, user: User, link: str, recipe: str):
        """
        Creates a CompositeMeal in the database.

        :param name: name of the meal
        :param user: User that created the meal
        :param link: link to the recipe
        :param recipe: recipe of the meal
        """
        self.name = name
        self.protein = 0
        self.carb = 0
        self.fat = 0
        self.user = user
        self.qty = 0
        self.link = link
        self.recipe = recipe
        self.saved = False
        self.units.append(CompositeMealUnit(description="grams", weight=1))

        db.session.add(self)
        db.session.commit()

    def set_qty(self, assoc: CompositeProductAssoc, new_qty: float) -> None:
        """
        Updates quantity of ProductMeal in CompositeMeal.

        :param assoc: CompositeProductAssoc that connects CompositeMeal to the ProductMeal
        :param new_qty: new quantity defined by editor
        :return: None
        """
        old_qty = assoc.qty
        assoc.qty = new_qty

        delta = assoc.qty - old_qty
        old_self_qty = self.qty
        self.qty = self.qty + delta

        # defining new macronutrient values per 100g
        self.carb = (self.carb * old_self_qty + delta * assoc.product.carb) / self.qty
        self.calories = (self.calories * old_self_qty + delta * assoc.product.calories) / self.qty
        self.protein = (self.protein * old_self_qty + delta * assoc.product.protein) / self.qty
        self.fat = (self.fat * old_self_qty + delta * assoc.product.fat) / self.qty

        db.session.commit()

        return None

    def clear(self) -> None:
        """
        Deletes all CompositeProductAssocs in Meal and changes macronutrient values to 0.

        :return: None
        """
        while self.products:
            assoc = self.products.pop()
            db.session.delete(assoc)
        self.calories = 0
        self.carb = 0
        self.protein = 0
        self.fat = 0
        self.qty = 0
        db.session.commit()

        return None

    def delete(self) -> None:
        """
        Deletes CompositeMeal from database.

        :return: None
        """
        self.clear()
        db.session.delete(self)
        db.session.commit()

        return None

    def save(self) -> None:
        """
        Changes 'saved' value of CompositeMeal to True, enabling adding to diet but disabling editing the meal.

        :return: None
        """
        self.saved = True
        db.session.commit()

        return None

    def add_product(self, product: ProductMeal, qty: float) -> None:
        """
        Adds a ProductMeal to CompositeMeal.

        :param product: ProductMeal that is added to CompositeMeal
        :param qty: weight of the added ProductMeal
        :return: None
        """
        assoc = CompositeProductAssoc(qty=0)
        assoc.product = product
        self.products.append(assoc)
        self.set_qty(assoc, qty)

        return None

    def copy(self, other):
        """
        Substitutes current data of CompositeMeal with a different CompositeMeal data.

        :param CompositeMeal other: CompositeMeal that is copied
        :return: None
        """
        while self.products:
            assoc = self.products.pop()
            db.session.delete(assoc)

        for assoc in other.products:
            new_assoc = CompositeProductAssoc()
            new_assoc.product = assoc.product
            new_assoc.qty = assoc.qty
            self.products.append(new_assoc)

        self.carb = other.carb
        self.calories = other.calories
        self.protein = other.protein
        self.fat = other.fat
        self.qty = other.qty
        self.recipe = other.recipe
        self.link = other.link
        db.session.commit()

        return None

    def remove_product(self, assoc: CompositeProductAssoc) -> None:
        """
        Removes ProductMeal from CompositeMeal.

        :param assoc: CompositeProductAssoc to be removed
        :return: None
        """
        if self.qty - assoc.qty != 0:
            self.set_qty(assoc, 0)
        else:
            self.carb = 0
            self.calories = 0
            self.fat = 0
            self.protein = 0

        self.products.remove(assoc)
        db.session.delete(assoc)
        db.session.commit()

        return None


class WeightMeal(Meal):
    """
    Represents meals with known macronutrient values per weight, but without products.
    """
    __tablename__ = "weight_meal"
    __mapper_args__ = {
        "polymorphic_identity": "weight_meal"
    }
    id = db.Column(db.Integer, db.ForeignKey("meal.id"), primary_key=True)
    link = db.Column(db.String(250))
    recipe = db.Column(db.Text)
    units = relationship("WeightMealUnit")

    def __init__(self, name, protein, carb, fat, user, link, recipe):
        """
        Creates a WeightMeal in the database.

        :param name: name of the meal
        :param protein: protein content per 100g
        :param carb: carb content per 100g
        :param fat: fat content per 100g
        :param user: User that created the meal
        :param link: link to the recipe
        :param recipe: recipe of the meal
        """
        self.name = name
        self.protein = protein
        self.carb = carb
        self.fat = fat
        self.user = user
        self.link = link
        self.recipe = recipe
        self.saved = True
        self.units.append(WeightMealUnit(description="grams", weight=1))

        db.session.add(self)
        db.session.commit()


class ServingMeal(Meal):
    """
    Represents meals with known macronutrient values per serving, but without products.
    """
    __tablename__ = "serving_meal"
    __mapper_args__ = {
        "polymorphic_identity": "serving_meal"
    }
    id = db.Column(db.Integer, db.ForeignKey("meal.id"), primary_key=True)
    link = db.Column(db.String(250))
    recipe = db.Column(db.Text)

    def __init__(self, name, protein, carb, fat, user, link, recipe):
        """
        Create a ServingMeal in the database.

        :param name: name of the meal
        :param protein: protein content per 100g
        :param carb: carb content per 100g
        :param fat: fat content per 100g
        :param user: User that created the meal
        :param link: link to the recipe
        :param recipe: recipe of the meal
        """
        self.name = name
        self.protein = protein
        self.carb = carb
        self.fat = fat
        self.user = user
        self.link = link
        self.recipe = recipe
        self.saved = True

        db.session.add(self)
        db.session.commit()


class MealUnit(db.Model):
    """
    Represents a unit of weight for meals (e.g. a spoon, a bowl, a cup)
    """
    __tablename__ = 'weight_unit'
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.String(250), nullable=False)
    weight = db.Column(db.Float, nullable=False)
    type = db.Column(db.String(20))

    __mapper_args__ = {
        "polymorphic_identity": "meal_unit",
        "polymorphic_on": type,
    }

    def __init__(self, description, weight):
        """
        Creates a unit of weight.

        :param description: short description of a unit
        :param weight: how much weight the unit contains in grams
        """
        self.description = description
        self.weight = weight

        db.session.add(self)
        db.session.commit()


class WeightMealUnit(MealUnit):
    __mapper_args__ = {
        "polymorphic_identity": "weight_meal_unit"
    }
    weight_meal_id = db.Column(db.Integer, db.ForeignKey("weight_meal.id"))


class ProductMealUnit(MealUnit):
    __mapper_args__ = {
        "polymorphic_identity": "product_meal_unit"
    }
    product_meal_id = db.Column(db.Integer, db.ForeignKey("product_meal.id"))


class CompositeMealUnit(MealUnit):
    __mapper_args__ = {
        "polymorphic_identity": "composite_meal_unit"
    }
    composite_meal_id = db.Column(db.Integer, db.ForeignKey("composite_meal.id"))


class DietMealAssoc(db.Model):
    """Association table to represent meals contained in particular diet days."""
    __tablename__ = "diet_meal_assoc"

    id = db.Column(db.Integer, index=True, primary_key=True, autoincrement=True)
    diet_id = db.Column(db.ForeignKey('diet.id'))
    meal_id = db.Column(db.ForeignKey('meal.id'))
    qty = db.Column(db.Float, nullable=False)
    meal = relationship("Meal")

    def edit_qty(self, new_qty: float) -> None:
        """
        Edits quantity for a Meal in Diet.

        :param new_qty: new quantity for chosen meal
        :return: None
        """
        self.qty = new_qty
        db.session.commit()

        return None


class Diet(db.Model):
    """
    Represents diet for a given day.

    Class has relationships with:
    - Meal class - many-to-many
    - User class - many-to-one
    """
    __tablename__ = 'diet'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = relationship('User', back_populates='diets')
    date = db.Column(db.Date, nullable=False)
    weight = db.Column(db.Float)
    meals = relationship("DietMealAssoc")

    @staticmethod
    def get_diets_in_current_month() -> List:
        """
        Returns list of the DayDiet objects in current month.

        :return: list of DayDiet objects
        """
        today = dt.date.today()
        first_day = dt.date(today.year, today.month, 1)
        last_day = dt.date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
        return Diet.query.filter(DayDiet.date.between(first_day, last_day)).all()

    def __init__(self, user: User, date: dt.date or str):
        """
        Creates a new Diet in database.

        :param user: owner of the diet day
        :param date: date of the diet
        """
        self.user_id = user.id
        self.user = user
        if type(date) == str:
            date = dt.datetime.strptime(date, "%Y-%m-%d").date()
        self.date = date

        db.session.add(self)
        db.session.commit()

    def copy(self, other) -> None:
        """
        Copies a Diet data from another date.

        :param Diet other: Diet that is copied
        :return: None
        """
        for assoc in other.meals:
            new_assoc = DietMealAssoc(qty=assoc.qty, meal=assoc.meal)
            self.meals.append(new_assoc)
        db.session.commit()

        return None

    def delete(self) -> None:
        """
        Deletes Diet from database.

        :return: None
        """
        db.session.delete(self)
        db.session.commit()

        return None

    def remove_meal(self, assoc: DietMealAssoc) -> None:
        """
        Deletes Meal from Diet.

        :param assoc: DietMealAssoc that connects Meal to Diet
        :return: None
        """
        self.meals.remove(assoc)
        db.session.delete(assoc)
        db.session.commit()

        return None

    def add_meal(self, qty: float, meal: Meal) -> None:
        """
        Adds Meal to Diet.

        :param meal: Meal to be added to Diet
        :param qty: number of grams/servings to be added, depending on the meal type
        :return: None
        """
        assoc = DietMealAssoc(qty=qty, meal=meal)
        self.meals.append(assoc)
        db.session.commit()

        return None

    def update_weight(self, weight: float) -> None:
        """
        Updates User weight for the day.

        :param weight: weight of the User
        :return: None
        """
        self.weight = weight
        db.session.commit()

        return None
