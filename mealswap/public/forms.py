from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, TextAreaField
from wtforms.validators import DataRequired, NumberRange


class ProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(message='Please fill in the data')])
    protein = FloatField('Proteins per 100g',
                         validators=[NumberRange(min=0, message='Please enter the value not less than 0')])
    carb = FloatField('Carbs per 100g',
                      validators=[NumberRange(min=0, message='Please enter the value not less than 0')])
    fat = FloatField('Fats per 100g',
                     validators=[NumberRange(min=0, message='Please enter the value not less than 0')])
    submit = SubmitField('Add product')

    def validate(self, **kwargs):
        initial_validation = super(ProductForm, self).validate()
        if not initial_validation:
            return False
        if self.protein.data == 0 and self.carb.data == 0 and self.fat.data == 0:
            self.protein.errors.append("At least one of the macronutrients has to be bigger than 0")
            return False
        return True


class EmptyMealForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(message='Please fill in the data')])
    protein = FloatField('Proteins per 100g',
                         validators=[NumberRange(min=0, message='Please enter the value not less than 0')])
    carb = FloatField('Carbs per 100g',
                      validators=[NumberRange(min=0, message='Please enter the value not less than 0')])
    fat = FloatField('Fats per 100g',
                     validators=[NumberRange(min=0, message='Please enter the value not less than 0')])
    link = StringField('Link to the recipe (optional)')
    recipe = TextAreaField('Recipe (optional)')
    submit = SubmitField('Add meal')

    def validate(self, **kwargs):
        initial_validation = super(EmptyMealForm, self).validate()
        if not initial_validation:
            return False
        if self.protein.data == 0 and self.carb.data == 0 and self.fat.data == 0:
            self.protein.errors.append("At least one of the macronutrients has to be bigger than 0")
            return False
        return True


class CompositeMealForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(message='Please fill in the data')])
