import os
from flask import Flask
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask import redirect, url_for


#load environment variables from .env
load_dotenv()

db = SQLAlchemy()

# manage user sessions
login_manager = LoginManager()

migrate = Migrate()

def create_app():

    app = Flask(__name__, instance_relative_config=True)

    # Load config from instance/config.py
    app.config.from_pyfile("config.py")

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")

    print("Using database file at:", app.config['SQLALCHEMY_DATABASE_URI'])
    # app = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key')
    # to connect flask app with sqlite database having file site.db 
    # app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
    # disables a feature that tracks every change to objects.
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # binds SQLAlchemy object here (db) with the flask app
    db.init_app(app)

    migrate.init_app(app, db)

    # binds the LoginManager to your app
    login_manager.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'

    from app.models import User

    # login_user(user) puts user.id into the session, and load_user(user_id) retrieves the full row from the User table using that ID. That full object becomes current_user
    @login_manager.user_loader
    def load_user(user_id):
        # returns the row based on the query having a specific user_id which becomes the current user logged in
        return User.query.get(int(user_id))

    # Register blueprints here - they are like mini applications 
    from app.auth.routes import auth_bp
    from app.user.routes import user_bp
    from app.swap.routes import swap_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(swap_bp)

    @app.route('/')
    def index():
        return redirect(url_for('swap.home'))
        
    return app
