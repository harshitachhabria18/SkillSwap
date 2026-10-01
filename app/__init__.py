import os
from flask import Flask
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask import redirect, url_for
from flask_wtf.csrf import CSRFProtect
import cloudinary

#load environment variables from .env
load_dotenv()

db = SQLAlchemy()
csrf = CSRFProtect()

# manage user sessions
login_manager = LoginManager()

migrate = Migrate()

def create_app():

    app = Flask(__name__, instance_relative_config=True)

    # Load config from instance/config.py
    app.config.from_pyfile("config.py")

    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("SQLALCHEMY_DATABASE_URI")

    # fix(5): raise a clear error instead of using a hardcoded fallback key
    secret_key = os.getenv('SECRET_KEY')
    if not secret_key:
        raise RuntimeError(
            "SECRET_KEY environment variable is not set. "
            "Add SECRET_KEY=<your-random-string> to your .env file."
        )
    app.config['SECRET_KEY'] = secret_key

    # disables a feature that tracks every change to objects.
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # fix(10): keep connections alive on Neon/Render (avoids idle-connection drops)
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }

    # binds SQLAlchemy object here (db) with the flask app
    db.init_app(app)

    # fix(2): enable CSRF protection globally for all POST forms
    csrf.init_app(app)

    cloudinary.config(
        cloud_name = os.getenv('CLOUDINARY_CLOUD_NAME'),
        api_key    = os.getenv('CLOUDINARY_API_KEY'),
        api_secret = os.getenv('CLOUDINARY_API_SECRET'),
        secure     = True
    )

    migrate.init_app(app, db)

    # binds the LoginManager to your app
    login_manager.init_app(app)

    login_manager.login_view = 'auth.login'
    login_manager.login_message = 'Please log in to access this page.'
    login_manager.login_message_category = 'warning'

    from app.models import User, Notification

    # login_user(user) puts user.id into the session, and load_user(user_id) retrieves the full row from the User table using that ID. That full object becomes current_user
    @login_manager.user_loader
    def load_user(user_id):
        # fix(6): db.session.get() is the SQLAlchemy 2.0 replacement for Query.get()
        return db.session.get(User, int(user_id))

    # Context processor: inject unread notification count into EVERY template automatically.
    # This is how the navbar bell badge gets its number without every route having to pass it.
    @app.context_processor
    def inject_notification_count():
        if current_user.is_authenticated:
            count = Notification.query.filter_by(
                user_id=current_user.id,
                is_read=False
            ).count()
            return {'unread_notification_count': count}
        return {'unread_notification_count': 0}

    # Register blueprints here - they are like mini applications
    from app.auth.routes import auth_bp
    from app.user.routes import user_bp
    from app.swap.routes import swap_bp
    from app.notif_routes import notif_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(swap_bp)
    app.register_blueprint(notif_bp)

    @app.route('/')
    def index():
        return redirect(url_for('swap.home'))
        
    return app
