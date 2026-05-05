from flask import Blueprint, render_template, redirect, url_for, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required
# import login and register child classes from form.py
from app.forms import RegisterForm, LoginForm
# import User table
from app.models import User
from app import db

# creating a blueprint for authentication (login and register) -> A blueprint is a small flask app which helps the main flask app to be divided into differnet modules
auth_bp = Blueprint('auth', __name__,url_prefix='/auth',template_folder='templates/auth')

# route for register page
@auth_bp.route("/register", methods=["GET","POST"])
def register():
    # here form is the object of RegisterForm class from forms.py
    form = RegisterForm()
    # to check if it is a POST request
    if form.validate_on_submit():
        # Check if user already exists
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash(message='Email already registered.', category='danger')
            # return back to register
            return redirect(url_for('auth.register'))

        # create new user
        # create a hashed password for security
        hashed_password = generate_password_hash(form.password.data)

        # create a new user for the User table and insert the data from the form in the User table
        new_user = User(
            name=form.name.data,
            email=form.email.data,
            password=hashed_password
        )

        # add the new user in the database session
        db.session.add(new_user)

        db.session.commit()

        flash(message='Registration successful. Please log in.', category='success')
        # once user registers, take to login page
        return redirect(url_for('auth.login'))
    
    # return the register.html page
    return render_template('register.html', form=form)

# route for login page
@auth_bp.route("/login", methods=["GET","POST"])
def login():
    # here form is the object of LoginForm class from forms.py
    form = LoginForm()

    # to check if it is a POST request
    if form.validate_on_submit():
        # filtering the email in the database entered by the user
        user = User.query.filter_by(email=form.email.data).first()

        # Check email first
        if not user:
            flash(message='No account found with that email.', category='danger')
            return render_template('login.html', form=form)

         # Then check password
        if not check_password_hash(user.password, form.password.data):
            flash(message='Incorrect password.', category='danger')
            return render_template('login.html', form=form)

        # Both correct — log in and go to Home page
        login_user(user)
        flash(message='Logged in successfully!', category='success')
        return redirect(url_for('swap.home'))  # ← goes to Screen 1


    return render_template('login.html', form=form)

# route for logout
@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash(message='You have been logged out.', category='info')
    # if user logsout, take it to login page
    return redirect(url_for('auth.login'))
