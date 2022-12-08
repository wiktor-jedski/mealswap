import pytest
import datetime as dt

from mealswap.models.models import *


@pytest.fixture(scope='module')
def new_user():
    user = User(email='email@email.com', password='password', name='username', confirmed=False)
    return user


@pytest.fixture(scope='module')
def new_diet(new_user):
    diet = DayDiet(new_user, date=dt.date.today())
    return diet
