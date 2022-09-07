"""App config"""
from dotenv import dotenv_values

env_config = dotenv_values("/home/wiktor/web/mealswap/mealswap/.env")
MAIL_DEFAULT_SENDER = env_config['MAIL_DEFAULT_SENDER']
MAIL_USERNAME = env_config['MAIL_USERNAME']
MAIL_PASSWORD = env_config['MAIL_PASSWORD']

SECRET_KEY = 'PLACEHOLDER'
BOOTSTRAP_BTN_STYLE = 'success'
SQLALCHEMY_DATABASE_URI = 'sqlite:///mealswap.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECURITY_PASSWORD_SALT = 'PLACEHOLDER'
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
