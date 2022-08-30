# from app import create_app
# from extensions import db
# from user.models import User
# import datetime as dt
# from flask.cli import FlaskGroup
#
# cli = FlaskGroup(create_app())
#
#
# @cli.command('create_db')
# def create_db():
#     db.create_all()
#
#
# @cli.command('create_admin')
# def create_admin():
#     db.session.add(User(
#         email='jedrzejewskiwiktor@gmail.com',
#         password='Mealswapjestzajebisty1!',
#         name='admin',
#         admin=True,
#         confirmed=True,
#         confirmed_on=dt.datetime.now()
#     ))
#     db.session.commit()


import click
from mealswap.extensions import db


@click.command(name='create')
def create():
    db.create_all()
