import click
from mealswap.extensions import db
from mealswap.models import User
from werkzeug.security import generate_password_hash
import datetime as dt


@click.command(name='create')
def create():
    db.create_all()


@click.command(name='add_admin')
@click.option('--email', prompt='Email')
@click.option('--password', prompt='Password')
def add_admin(email, password):
    admin = User(email=email,
                 password=generate_password_hash(password),
                 name='admin',
                 confirmed=True,
                 admin=True,
                 confirmed_on=dt.datetime.now())
    db.session.add(admin)
    db.session.commit()
