from flask import Flask
from mealswap import commands
from mealswap.controllers import add, diet, edit, public, rate, search, user
from mealswap.controllers.controls import get_element_by_id, Model
from mealswap.extensions import (
    login_manager,
    db,
    Bootstrap4,
    mail
)


def create_app(config='mealswap.settings') -> Flask:
    """
    Create app factory.

    :param config: config object to be used.
    :return: Flask app
    """
    app = Flask(__name__.split(".")[0])
    app.config.from_object(config)
    register_extensions(app)
    register_blueprints(app)
    register_commands(app)
    return app


def register_extensions(app):
    """Registers app extensions."""
    login_manager.init_app(app)
    db.init_app(app)
    Bootstrap4(app)
    mail.init_app(app)
    return None


def register_blueprints(app):
    """Registers Flask blueprints"""
    app.register_blueprint(add.views.blueprint)
    app.register_blueprint(diet.views.blueprint)
    app.register_blueprint(edit.views.blueprint)
    app.register_blueprint(public.views.blueprint)
    app.register_blueprint(rate.views.blueprint)
    app.register_blueprint(search.views.blueprint)
    app.register_blueprint(user.views.blueprint)
    return None


def register_commands(app):
    """Registers Click commands"""
    app.cli.add_command(commands.create)
    app.cli.add_command(commands.add_admin)
    app.cli.add_command(commands.import_meals)
    return None


@login_manager.user_loader
def load_user(user_id: str) -> db.Model or None:
    """Loads current user.

    :param user_id: id of the user that is logged in
    :return: User object or None (if not logged in)
    """
    return get_element_by_id(Model.USER, user_id)
