import os
from flask import Flask
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

#load environment variables from .env
load_dotenv()

db = SQLAlchemy()

# manage user sessions
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return None

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    # to connect flask app with sqlite database having file site.db 
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    # disables a feature that tracks every change to objects.
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # binds SQLAlchemy object here (db) with the flask app
    db.init_app(app)

    # binds the LoginManager to your app
    login_manager.init_app(app)

    # Register blueprints here - they are like mini applications 
    from app.auth.routes import auth_bp
    # from app.user.routes import user_bp
    from app.swap.routes import swap_bp

    app.register_blueprint(auth_bp)
    # app.register_blueprint(user_bp)
    app.register_blueprint(swap_bp)

    return app
