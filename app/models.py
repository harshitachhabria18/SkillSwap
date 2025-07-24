from app import db
from flask_login import UserMixin

# db.Model is the base class and User is the name of the child class (here User table)
class User(db.Model, UserMixin):
    # all the below are the fields or columns for the User table
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    location = db.Column(db.String(200))
    profile_photo = db.Column(db.String(255)) # storage of file name
    availability = db.Column(db.String(100))
    session_duration = db.Column(db.String(50))
    profile_visibility = db.Column(db.String(50))
