import click
from mealswap.extensions import db
from mealswap.models import User, Item, Product, ItemProductAssoc
from werkzeug.security import generate_password_hash
import datetime as dt
import csv


@click.command(name='create')
def create():
    """Creates all database tables."""
    db.create_all()
    return None


@click.command(name='add_admin')
@click.option('--email', prompt='Email')
@click.option('--password', prompt='Password')
def add_admin(email: str, password: str):
    """Adds an admin user"""
    admin = User(email=email,
                 password=generate_password_hash(password),
                 name='admin',
                 confirmed=True,
                 admin=True,
                 confirmed_on=dt.datetime.now())
    db.session.add(admin)
    db.session.commit()
    return None


@click.command(name='import_meals')
@click.option('--file', prompt='File directory')
@click.option('--email', prompt='Added by user (email)')
def import_meals(file: str, email: str):
    """
    Imports meals from a .csv file.
    Function uses following columns: name, protein, carbohydrates, fat, link

    :param file: filename of the .csv file
    :param email: Email address of the user adding the data.
    """
    with open(file, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        user = db.session.query(User).filter(User.email == email).first()
        if not user:
            print('User not found')
            return -1
        for row in reader:
            item = Item(name=row['name'],
                        protein=float(row['protein']),
                        carb=float(row['carbohydrates']),
                        fat=float(row['fat']),
                        user=user,
                        has_weight=False,
                        link=row['link'],
                        saved=True,
                        qty=1,
                        servings=1)
            db.session.add(item)
        db.session.commit()
        return None


@click.command(name='import_products')
@click.option('--file', prompt='File directory')
@click.option('--email', prompt='Added by user (email)')
def import_products(file: str, email: str):
    """
    Imports products from a .csv file.
    Function uses following columns: name, protein, carbohydrates, fat

    :param file: filename of the .csv file
    :param email: Email address of the user adding the data.
    """
    with open(file, 'r', newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        user = db.session.query(User).filter(User.email == email).first()
        if not user:
            print('User not found')
            return -1
        for row in reader:
            product = Product(
                name=row['name'],
                protein=float(row['protein']),
                carb=float(row['carbohydrates']),
                fat=float(row['fat'])
            )
            item = Item(
                name=row['name'],
                protein=float(row['protein']),
                carb=float(row['carbohydrates']),
                fat=float(row['fat']),
                has_weight=True,
                user=user,
                qty=0,
                servings=0,
                saved=True
            )
            db.session.add(product)
            assoc = ItemProductAssoc(qty=100)
            assoc.product = product
            item.products.append(assoc)
            db.session.add(item)
        db.session.commit()
        return None
