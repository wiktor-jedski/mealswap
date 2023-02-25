"""App config"""
from dotenv import dotenv_values

env_config = dotenv_values("mealswap/.env")
MAIL_DEFAULT_SENDER = env_config['MAIL_DEFAULT_SENDER']
MAIL_USERNAME = env_config['MAIL_USERNAME']
MAIL_PASSWORD = env_config['MAIL_PASSWORD']
SECRET_KEY = env_config['SECRET_KEY']
SECURITY_PASSWORD_SALT = env_config['SECURITY_PASSWORD_SALT']
SQLALCHEMY_DATABASE_URI = env_config['SQLALCHEMY_DATABASE_URI']

BOOTSTRAP_BTN_STYLE = 'success'
SQLALCHEMY_TRACK_MODIFICATIONS = False
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
