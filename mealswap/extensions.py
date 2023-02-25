from flask_login import LoginManager
from flask_bootstrap import Bootstrap4
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail

login_manager = LoginManager()
db = SQLAlchemy()
mail = Mail()
