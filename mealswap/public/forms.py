from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, TextAreaField, DateField, DecimalField, BooleanField
from wtforms.validators import DataRequired, NumberRange, Optional


class ProductForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(message='Please fill in the data')])
    protein = FloatField('Proteins per 100g',
                         validators=[NumberRange(min=0, message='Please enter the value not less than 0')])
    carb = FloatField('Carbs per 100g',
                      validators=[NumberRange(min=0, message='Please enter the value not less than 0')])
    fat = FloatField('Fats per 100g',
                     validators=[NumberRange(min=0, message='Please enter the value not less than 0')])
    submitProductForm = SubmitField('Add product')

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
                         validators=[NumberRange(min=0, max=100, message='Please enter the value between 0 and 100')])
    carb = FloatField('Carbs per 100g',
                      validators=[NumberRange(min=0, max=100, message='Please enter the value between 0 and 100')])
    fat = FloatField('Fats per 100g',
                     validators=[NumberRange(min=0, max=100, message='Please enter the value between 0 and 100')])
    link = StringField('Link to the recipe (optional)')
    recipe = TextAreaField('Recipe (optional)')
    submitEmptyMealForm = SubmitField('Add meal')

    def validate(self, **kwargs):
        initial_validation = super(EmptyMealForm, self).validate()
        if not initial_validation:
            return False
        if self.protein.data == 0 and self.carb.data == 0 and self.fat.data == 0:
            self.protein.errors.append("At least one of the macronutrients has to be bigger than 0")
            return False
        if self.protein.data + self.carb.data + self.fat.data > 100:
            self.protein.errors.append("Macronutrients sum has to be lower than 100 per 100g")
            return False
        return True


class CompositeMealForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(message='Please fill in the data')])
    link = StringField('Link to the recipe (optional)')
    recipe = TextAreaField('Recipe (optional)')
    submitCompositeMealForm = SubmitField('Create composite meal')


class SearchForm(FlaskForm):
    search = StringField('Search for:', validators=[DataRequired()])
    submitSearchForm = SubmitField('Search')


class QtyForm(FlaskForm):
    qty = FloatField('Qty (g):', validators=[DataRequired(), NumberRange(min=0, message='Qty cannot be negative')])
    submitQtyForm = SubmitField('Add')


class DateQtyForm(FlaskForm):
    date = DateField('Enter date:', validators=[DataRequired()])
    qty = FloatField('Qty (g):', validators=[DataRequired(), NumberRange(min=0, message='Qty cannot be negative')])
    submitDateQtyForm = SubmitField('Add')


class DiscoverForm(FlaskForm):
    submitDiscoverForm = SubmitField('Discover')


class MacroForm(FlaskForm):
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
        print(self.fat.data)
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
    qty = FloatField('New qty:', validators=[DataRequired(), NumberRange(min=0, message='Qty cannot be negative')])
    submitEditForm = SubmitField('Edit')


class DeleteForm(FlaskForm):
    submitDeleteForm = SubmitField('Delete')


class SaveForm(FlaskForm):
    submitSaveForm = SubmitField('Save')


class CopyMealForm(FlaskForm):
    search = StringField('Search for:', validators=[DataRequired()])
    submitCopyMealForm = SubmitField('Search')
