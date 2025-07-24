from flask_wtf import FlaskForm
# wtforms contain differnt types of field same as type=text,number etc in the html forms
from wtforms import StringField, PasswordField, SubmitField
# validators automatically validates the fields and gives persoal message if defined by User
from wtforms.validators import DataRequired, Email, Length, EqualTo

# here FlaskForm is the default python base class having properties of Forms in python and LoginForm is the child class containing the fields or properties to be added in the login form
class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

# here FlaskForm is the default python base class having properties of Forms in python and RegisterForm is the child class containing the fields or properties to be added in the register form
class RegisterForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match.') # like added here
    ])
    submit = SubmitField('Register')