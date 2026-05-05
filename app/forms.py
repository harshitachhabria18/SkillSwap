from flask_wtf import FlaskForm
# wtforms contain differnt types of field same as type=text,number etc in the html forms
from wtforms import StringField, PasswordField, SubmitField, SelectField, SelectMultipleField
# validators automatically validates the fields and gives persoal message if defined by User
from wtforms.validators import DataRequired, Email, Length, EqualTo
# FileField to upload files and FileAllowed to apply validators on the file type
from flask_wtf.file import FileField, FileAllowed

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

# here FlaskForm is the default python base class having properties of Forms in python and EditProfileForm is the child class containing the fields or properties to be added in the EditProfile form
class EditProfileForm(FlaskForm):
    # the photo field contains the profile photo of the user added by using FileField in the form
    photo = FileField('Add/Edit Photo', validators=[
        # here FileAllowed checks the file uploaded should be of image format only
        FileAllowed(['jpg', 'png', 'jpeg'], 'Images only!')])
    name = StringField('Full Name', validators=[DataRequired()])
    location = StringField('Location', validators=[DataRequired()])
    # skills offered has SelectField type which helps to select a option(dropdown) just like in HTML forms
    # choices is filled dynamically by the skills table from the database
    # coerce = int helps to send data in [(1, 'Python'), (2, 'Web Design')] type where first one is the id for a specific skill
    skills_offered = SelectMultipleField("Skills Offered",choices=[],coerce=int)
    skills_wanted = SelectMultipleField("Skills Wanted",choices=[],coerce=int,)
    # here first value is submitted as the value and the second value is shown on UI
    availability = SelectField("Availability", choices=[
        ('Weekdays', 'Weekdays'),
        ('Weekends', 'Weekends'),
        ('Evenings', 'Evenings'),
        ('Flexible', 'Flexible')
    ], validators=[DataRequired()])
    # here first value is submitted and second valu is shown in dropdown in UI
    session_duration = SelectField("Session Duration", choices=[
        ("30", "30 minutes"),
        ("45", "45 minutes"),
        ("60", "1 hour"),
        ("90", "1.5 hours"),
        ("120", "2 hours"),
    ], validators=[DataRequired()])
    # here first value is submitted as the value and the second value is shown on UI
    profile_type = SelectField("Profile Type", choices=[
        ('Public', 'Public'),
        ('Private', 'Private')
    ], validators=[DataRequired()])
    # submit field to Save the form
    submit = SubmitField('Save')

