from flask import Flask

from mealswap import public, user, commands
from mealswap.extensions import (
    login_manager,
    db,
    Bootstrap4,
)


def create_app(config='mealswap.settings'):
    """Create app factory.
    @:param config: config object to be used.
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
    return None


def register_blueprints(app):
    """Registers Flask blueprints"""
    app.register_blueprint(public.views.blueprint)
    app.register_blueprint(user.views.blueprint)
    return None


def register_commands(app):
    """Registers Click commands"""
    app.cli.add_command(commands.create)
