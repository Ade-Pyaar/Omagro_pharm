from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from sales_project.models import User, Products
from flask_login import current_user


class Regform(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

    def validate_name(self, name):
        user = User.query.filter_by(name=name.data).first()
        if user:
            raise ValidationError('That username is taken.')


class Loginform(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class Updateform(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Update')

    def validate_name(self, name):
        if name.data != current_user.name:
            user = User.query.filter_by(name=name.data).first()
            if user:
                raise ValidationError('That username is taken.')


class RequestResetForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    submit = SubmitField('Request Password Reset')

    def validate_name(self, name):
        user = User.query.filter_by(name=name.data).first()
        if user is None:
            raise ValidationError('There is no account with that name.')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')


class NewProductForm(FlaskForm):
    name = StringField('Name of item', validators=[DataRequired()])
    price = IntegerField('Price', validators=[DataRequired()])
    submit = SubmitField('Edit Product')


class EditProductForm(FlaskForm):
    name = StringField('Name of item', validators=[DataRequired()])
    price = IntegerField('Price', validators=[DataRequired()])
    submit = SubmitField('Edit Product')

    def validate_name(self, name):
        item = Products.query.filter_by(name=name.data).first()
        if item:
            raise ValidationError('This product already exists.')