import click
from mealswap.extensions import db
from mealswap.models import User, Item, Product, ItemProductAssoc
from werkzeug.security import generate_password_hash
import datetime as dt
import csv


@click.command(name='create')
def create() -> None:
    """Creates all database tables.

    :return: None
    """
    db.create_all()
    return None


@click.command(name='add_admin')
@click.option('--name', prompt='Name')
@click.option('--email', prompt='Email')
@click.option('--password', prompt='Password')
def add_admin(name: str, email: str, password: str) -> None:
    """Adds an admin user

    :param name: admin name
    :param email: admin email address
    :param password: admin password
    :return: None
    """
    admin = User(email=email,
                 password=generate_password_hash(password),
                 name=name,
                 confirmed=True,
                 admin=True,
                 confirmed_on=dt.datetime.now())
    db.session.add(admin)
    db.session.commit()
    return None


@click.command(name='import_meals')
@click.option('--file', prompt='File directory')
@click.option('--email', prompt='Added by user (email)')
def import_meals(file: str, email: str) -> None or int:
    """
    Imports meals from a .csv file.
    Function uses following columns: name, protein, carbohydrates, fat, link

    :param file: filename of the .csv file
    :param email: Email address of the user adding the data.
    :return: -1 if user has not been found, None otherwise
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
def import_products(file: str, email: str) -> None or int:
    """
    Imports products from a .csv file.
    Function uses following columns: name, protein, carbohydrates, fat

    :param file: filename of the .csv file
    :param email: Email address of the user adding the data.
    :return: -1 if user has not been found, None otherwise
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
                fat=float(row['fat']),
                weight_per_ea=0
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
