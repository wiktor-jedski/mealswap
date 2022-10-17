from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, DateField, FloatField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange
from mealswap.models import User


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    name = StringField('Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirmation = PasswordField('Confirm password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Create New User')

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self, **kwargs):
        initial_validation = super(RegisterForm, self).validate()
        if not initial_validation:
            return False
        user = User.query.filter_by(email=self.email.data).first()
        if user:
            self.email.errors.append("Email already registered")
            return False
        return True


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self, **kwargs):
        initial_validation = super(LoginForm, self).validate()
        if not initial_validation:
            return False

        self.user = User.query.filter_by(email=self.email.data).first()
        if not self.user:
            self.email.errors.append("Email not found")
            return False

        if not self.user.check_password(self.password.data):
            self.password.errors.append("Wrong password")
            return False

        if not self.user.confirmed:
            self.email.errors.append("User not activated")
            return False

        return True


class DateForm(FlaskForm):
    date = DateField('Enter date:', validators=[DataRequired()])
    submit = SubmitField('Find')

    def __init__(self, *args, **kwargs):
        super(DateForm, self).__init__(*args, **kwargs)


class SearchForm(FlaskForm):
    search = StringField('Search for:', validators=[DataRequired()])
    submit = SubmitField('Search')

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)


class QtyForm(FlaskForm):
    qty = FloatField('Qty (g):', validators=[DataRequired(), NumberRange(min=0, message='Qty cannot be negative')])
    submit = SubmitField('Add')


class DeleteForm(FlaskForm):
    confirm = BooleanField('', validators=[DataRequired()])
    submit = SubmitField('Delete')


class EditForm(FlaskForm):
    qty = FloatField('New qty:', validators=[DataRequired(), NumberRange(min=0, message='Qty cannot be negative')])
    submit = SubmitField('Edit')
