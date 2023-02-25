from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, DateField, DecimalField, BooleanField, \
    PasswordField, IntegerField
from wtforms.validators import DataRequired, NumberRange, Optional, URL, Email, Length, EqualTo
from mealswap.controllers.controls import get_user_by_email


class ProductForm(FlaskForm):
    """A class used to create forms for product data"""
    name = StringField('Name', validators=[DataRequired(message='Please fill in the data')])
    protein = DecimalField('Proteins per 100g',
                           validators=[NumberRange(min=0, max=100, message='Please enter the value between 0 and 100')])
    carb = DecimalField('Carbs per 100g',
                        validators=[NumberRange(min=0, max=100, message='Please enter the value between 0 and 100')])
    fat = DecimalField('Fats per 100g',
                       validators=[NumberRange(min=0, max=100, message='Please enter the value between 0 and 100')])
    weight_per_ea = DecimalField('Weight per ea (optional)',
                                 validators=[NumberRange(min=0,
                                                         message='Please enter the value bigger than 0'), Optional()])
    submitProductForm = SubmitField('Add product')

    def validate(self, **kwargs):
        initial_validation = super(ProductForm, self).validate()
        if not initial_validation:
            return False
        if self.protein.data == 0 and self.carb.data == 0 and self.fat.data == 0:
            self.protein.errors.append("At least one of the macronutrients has to be bigger than 0")
            return False
        if self.protein.data + self.carb.data + self.fat.data > 100:
            self.protein.errors.append("Macronutrients sum has to be lower than 100 per 100g")
            return False
        return True


class WeightMealForm(FlaskForm):
    """A class used to create forms for meals with known macronutrient values per 100g"""
    name = StringField('Name', validators=[DataRequired(message='Please fill in the data')])
    protein = DecimalField('Proteins per 100g',
                           validators=[NumberRange(min=0, max=100, message='Please enter the value between 0 and 100')])
    carb = DecimalField('Carbs per 100g',
                        validators=[NumberRange(min=0, max=100, message='Please enter the value between 0 and 100')])
    fat = DecimalField('Fats per 100g',
                       validators=[NumberRange(min=0, max=100, message='Please enter the value between 0 and 100')])
    qty = DecimalField('Weight per serving (optional)',
                       validators=[Optional(), NumberRange(min=0, message='Weight must be bigger than 0')])
    link = StringField('Link to the recipe (optional)', validators=[URL(), Optional()])
    recipe = TextAreaField('Recipe (optional)')
    submitWeightMealForm = SubmitField('Add meal')

    def validate(self, **kwargs):
        initial_validation = super(WeightMealForm, self).validate()
        if not initial_validation:
            return False
        if self.protein.data == 0 and self.carb.data == 0 and self.fat.data == 0:
            self.protein.errors.append("At least one of the macronutrients has to be bigger than 0")
            return False
        if self.protein.data + self.carb.data + self.fat.data > 100:
            self.protein.errors.append("Macronutrients sum has to be lower than 100 per 100g")
            return False
        return True


class ServingMealForm(FlaskForm):
    """A class used to create forms for meals with known macronutrient values per serving"""
    name = StringField('Name', validators=[DataRequired(message='Please fill in the data')])
    protein = DecimalField('Proteins per serving',
                           validators=[NumberRange(min=0, message='Macronutrient value must be at least 0')])
    carb = DecimalField('Carbs per serving',
                        validators=[NumberRange(min=0, message='Macronutrient value must be at least 0')])
    fat = DecimalField('Fats per serving',
                       validators=[NumberRange(min=0, message='Macronutrient value must be at least 0')])
    link = StringField('Link to the recipe (optional)', validators=[URL(), Optional()])
    recipe = TextAreaField('Recipe (optional)')
    submitServingMealForm = SubmitField('Add meal')

    def validate(self, **kwargs):
        initial_validation = super(ServingMealForm, self).validate()
        if not initial_validation:
            return False
        if self.protein.data == 0 and self.carb.data == 0 and self.fat.data == 0:
            self.protein.errors.append("At least one of the macronutrients has to be bigger than 0")
            return False
        return True


class CompositeMealForm(FlaskForm):
    """A class used to create a composite meal (meal built out of products) via user input"""
    name = StringField('Name', validators=[DataRequired(message='Please fill in the data')])
    link = StringField('Link to the recipe (optional)', validators=[URL(), Optional()])
    recipe = TextAreaField('Recipe (optional)')
    submitCompositeMealForm = SubmitField('Create composite meal')


class SearchForm(FlaskForm):
    """A class used to create forms searching the database"""
    search = StringField('Search for:', validators=[DataRequired()])
    submitSearchForm = SubmitField('Search')


class QtyEaForm(FlaskForm):
    """A class used to create quantity/ea forms to add new items into diet or products into meals"""
    qty = DecimalField('Qty (g):', validators=[NumberRange(min=0, message='Qty cannot be negative')])
    ea = IntegerField('Qty (ea)', validators=[NumberRange(min=0, message='Qty cannot be negative')])
    submitQtyEaForm = SubmitField('Add')

    def validate(self, **kwargs):
        initial_validation = super(QtyEaForm, self).validate()
        if not initial_validation:
            return False
        if self.qty.data == 0 and self.ea.data == 0:
            self.qty.errors.append("Either qty in grams or ea has to be bigger than 0")
            self.ea.errors.append("Either qty in grams or ea has to be bigger than 0")
            return False
        if self.qty.data > 0 and self.ea.data > 0:
            self.qty.errors.append("Please fill only one field - either qty in gram or in ea.")
            self.ea.errors.append("Please fill only one field - either qty in gram or in ea.")
        return True


class DateQtyEaForm(FlaskForm):
    """A class used to create form for adding a meal replacement to a chosen day"""
    date = DateField('Enter date:', validators=[DataRequired()])
    qty = DecimalField('Qty (g):', validators=[NumberRange(min=0, message='Qty cannot be negative')])
    ea = IntegerField('Qty (ea):', validators=[NumberRange(min=1, message='Qty cannot be negative')])
    submitDateQtyForm = SubmitField('Add')


class DiscoverForm(FlaskForm):
    """A class used to create form for starting random meal rating"""
    submitDiscoverForm = SubmitField('Discover')


class MacroForm(FlaskForm):
    """A class used to create form for searching meal replacement"""
    protein = DecimalField('Proteins per 100g',
                           validators=[NumberRange(min=0, max=100, message='Please enter the value between 0 and 100'),
                                       Optional()])
    carb = DecimalField('Carbs per 100g',
                        validators=[NumberRange(min=0, max=100, message='Please enter the value between 0 and 100'),
                                    Optional()])
    fat = DecimalField('Fats per 100g',
                       validators=[NumberRange(min=0, max=100, message='Please enter the value between 0 and 100'),
                                   Optional()])
    calories = DecimalField('Calories per 100g',
                            validators=[Optional(), NumberRange(min=0)])
    submitMacroForm = SubmitField('Search')

    def validate(self, **kwargs):
        initial_validation = super(MacroForm, self).validate()
        empty_count = 0
        if self.protein.data is None:
            empty_count += 1
            self.protein.errors.append("At least two fields have to be filled")
        if self.carb.data is None:
            empty_count += 1
            self.carb.errors.append("At least two fields have to be filled")
        if self.fat.data is None:
            empty_count += 1
            self.fat.errors.append("At least two fields have to be filled")
        if self.calories.data is None:
            empty_count += 1
            self.calories.errors.append("At least two fields have to be filled")
        if not initial_validation:
            return False
        if empty_count > 2:
            return False
        return True


class EditForm(FlaskForm):
    """A class used to create quantity forms for editing"""
    qty = DecimalField('New qty (g):',
                       validators=[DataRequired(), NumberRange(min=0, message='Qty cannot be negative')])
    submitEditForm = SubmitField('Edit')


class EaEditForm(FlaskForm):
    """A class used to create ea forms for editing (for meals that do not have weight)"""
    qty = IntegerField('New qty (ea):',
                       validators=[DataRequired(), NumberRange(min=1, message='Qty cannot be negative')])
    submitEditForm = SubmitField('Edit')


class DeleteForm(FlaskForm):
    """Simple delete form"""
    submitDeleteForm = SubmitField('Delete')


class SaveForm(FlaskForm):
    """Simple save form"""
    submitSaveForm = SubmitField('Save')


class CopyMealForm(FlaskForm):
    """A class used to create search form for copying meals.
    A separate class has been created to remove bug regarding the same name of submit field.
    """
    search = StringField('Search for:', validators=[DataRequired()])
    submitCopyMealForm = SubmitField('Search')


class LinkRecipeServingsForm(FlaskForm):
    """A class used to create form for additional meal information"""
    link = StringField('Link to the recipe (optional)', validators=[URL(), Optional()])
    recipe = TextAreaField('Recipe (optional)')
    servings = IntegerField('Number of servings (default: 1)',
                            validators=[NumberRange(min=1, message='Number of servings cannot be smaller than 1'),
                                        Optional()])
    submitLinkRecipeForm = SubmitField('Save Optional Data')


class RatingForm(FlaskForm):
    """Simple form for ratings"""
    submitYumRatingForm = SubmitField('😋\nYum')
    submitMehRatingForm = SubmitField('😑\nMeh')
    submitYuckRatingForm = SubmitField('🤮\nYuck')


class RegisterForm(FlaskForm):
    """A class used to create registration form"""
    email = StringField('Email', validators=[DataRequired(), Email()])
    name = StringField('Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirmation = PasswordField('Confirm password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match')])
    submit = SubmitField('Create Account')

    def __init__(self, *args, **kwargs):
        super(RegisterForm, self).__init__(*args, **kwargs)
        self.user = None

    def validate(self, **kwargs):
        initial_validation = super(RegisterForm, self).validate()
        if not initial_validation:
            return False
        user = get_user_by_email(self.email.data)
        if user:
            self.email.errors.append("Email already registered")
            return False
        return True


class LoginForm(FlaskForm):
    """A class used to create login form"""
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

        self.user = get_user_by_email(self.email.data)
        if not self.user:
            self.email.errors.append("Email not found")
            return False

        if not self.user.check_password(self.password.data):
            self.password.errors.append("Wrong password")
            return False

        if not self.user.confirmed:
            self.email.errors.append("User not activated or account terminated")
            return False

        return True


class DateForm(FlaskForm):
    """A class used to create a date lookup form"""
    date = DateField('Enter date:', validators=[DataRequired()])
    submit = SubmitField('Find')


class ChangePasswordForm(FlaskForm):
    """A class used to create a form for password change"""
    password = PasswordField('Current password', validators=[DataRequired()])
    new_password = PasswordField('New password', validators=[DataRequired(), Length(min=8)])
    confirmation = PasswordField('Confirm password', validators=[
        DataRequired(), EqualTo('new_password', message='Passwords must match')])
    submit = SubmitField('Confirm')

    def __init__(self, user, *args, **kwargs):
        super(ChangePasswordForm, self).__init__(*args, **kwargs)
        self.user = user

    def validate(self, **kwargs):
        initial_validation = super(ChangePasswordForm, self).validate()
        if not initial_validation:
            return False

        if not self.user.check_password(self.password.data):
            self.password.errors.append("Wrong password")
            return False

        return True


class DeleteAccountForm(FlaskForm):
    """A class used to create a form for account termination"""
    password = PasswordField('Password', validators=[DataRequired()])
    confirmation = PasswordField('Confirm password', validators=[
        DataRequired(), EqualTo('password', message='Passwords must match')])
    submitDeleteAccountForm = SubmitField('Delete')

    def __init__(self, user, *args, **kwargs):
        super(DeleteAccountForm, self).__init__(*args, **kwargs)
        self.user = user

    def validate(self, **kwargs):
        initial_validation = super(DeleteAccountForm, self).validate()
        if not initial_validation:
            return False

        if not self.user.check_password(self.password.data):
            self.password.errors.append("Wrong password")
            return False

        return True


class DietGoalPercentageForm(FlaskForm):
    """A class used to create a form for setting diet goals based on percentages"""
    calories = DecimalField('Calories (kcal)', validators=[DataRequired(),
                                                           NumberRange(min=1, message="Number has to be positive")])
    protein = IntegerField('Protein (%)',
                           validators=[DataRequired(),
                                       NumberRange(min=0, max=100, message="Value has to be between 0 and 100")])
    carb = IntegerField('Carbohydrate (%)',
                        validators=[DataRequired(),
                                    NumberRange(min=0, max=100, message="Value has to be between 0 and 100")])
    fat = IntegerField('Fat (%)',
                       validators=[DataRequired(),
                                   NumberRange(min=0, max=100, message="Value has to be between 0 and 100")])
    submitDietGoalPercentageForm = SubmitField('Submit')

    def validate(self, **kwargs):
        initial_validation = super(DietGoalPercentageForm, self).validate()
        if not initial_validation:
            return False

        if self.protein.data + self.carb.data + self.fat.data != 100:
            self.protein.errors.append("Sum of percentages has to be 100")
            self.carb.errors.append("Sum of percentages has to be 100")
            self.fat.errors.append("Sum of percentages has to be 100")
            return False

        return True


class DietGoalMacroForm(FlaskForm):
    """A class used to create a form for setting diet goals based on concrete numbers"""
    calories = DecimalField('Calories (kcal)',
                            validators=[Optional(), NumberRange(min=0, message="Number has to be positive")])
    protein = DecimalField('Protein (g)',
                           validators=[Optional(), NumberRange(min=0, message="Number has to be positive")])
    carb = DecimalField('Carbohydrate (g)',
                        validators=[Optional(), NumberRange(min=0, message="Number has to be positive")])
    fat = DecimalField('Fat (g)',
                       validators=[Optional(), NumberRange(min=0, message="Number has to be positive")])
    submitDietGoalMacroForm = SubmitField('Submit')

    def validate(self, **kwargs):
        initial_validation = super(DietGoalMacroForm, self).validate()
        if not initial_validation:
            return False

        if self.protein.data is None:
            protein_check = 0
        else:
            protein_check = self.protein.data
        if self.carb.data is None:
            carb_check = 0
        else:
            carb_check = self.carb.data
        if self.fat.data is None:
            fat_check = 0
        else:
            fat_check = self.fat.data
        if self.calories.data is None:
            calories_check = 0
        else:
            calories_check = self.calories.data
        if protein_check * 4 + carb_check * 4 + fat_check * 9 > calories_check:
            self.calories.errors.append("Calories from macronutrients are bigger than goal calories. "
                                        "Please change one of them")
            return False

        return True


class WeightForm(FlaskForm):
    weight = DecimalField('Your Weight (kg):', validators=[NumberRange(min=0, message="Number has to be positive")])
    submitWeightForm = SubmitField('Update')
