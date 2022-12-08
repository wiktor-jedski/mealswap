import datetime as dt

from mealswap.models.models import *
from mealswap.tests.conftest import new_user
from mealswap.extensions import db


# User Model
def test_new_user(new_user):
    """
    GIVEN a User Model
    WHEN a new User is created
    THEN check the email, password, name, admin, registered_on, confirmed, confirmed_on fields
    """
    assert new_user.email == 'email@email.com'
    assert new_user.password != 'password'
    assert new_user.name == 'username'
    assert new_user.confirmed == False
    assert new_user.admin == False
    assert new_user.registered_on.date() == dt.date.today()
    assert new_user.confirmed_on is None


def test_set_password(new_user):
    """
    GIVEN a User Model
    WHEN a User changes password
    THEN the new hash is different from the previous hash
    """
    old_hash = new_user.password
    new_user.set_password('newpassword')
    assert new_user.password != old_hash


def test_check_password(new_user):
    """
    GIVEN a User Model
    WHEN the User's password is checked
    THEN return True if passwords match, False if they don't match
    """
    assert new_user.check_password('password') == True
    assert new_user.check_password('something') == False


def test_delete_account(new_user):
    """
    GIVEN a User Model
    WHEN a User deletes account
    THEN confirmed field is False
    """
    new_user.delete_account()
    assert new_user.confirmed == False


# DayDiet model
def test_new_diet(new_diet, new_user):
    """
    GIVEN a DayDiet Model
    WHEN a Diet is created
    THEN check the user_id, date fields
    """
    assert new_diet.user == new_user
    assert new_diet.user_id == new_user.id
    assert new_diet.date == dt.date.today()
