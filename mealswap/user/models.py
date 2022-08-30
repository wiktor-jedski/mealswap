import datetime as dt
from mealswap.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


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
