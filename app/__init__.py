import os
from flask import Flask
from dotenv import load_dotenv
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, current_user
from flask_migrate import Migrate
from flask import redirect, url_for
from flask_wtf.csrf import CSRFProtect
from flask_mail import Mail
from werkzeug.middleware.proxy_fix import ProxyFix
import cloudinary
from zoneinfo import ZoneInfo
from datetime import timezone

#load environment variables from .env
load_dotenv()

db = SQLAlchemy()
csrf = CSRFProtect()
mail = Mail()

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

    # Brevo API configuration
    app.config['BREVO_API_KEY'] = os.environ.get('BREVO_API_KEY')
    app.config['MAIL_SENDER'] = os.environ.get('MAIL_SENDER', 'noreply@skillswap.com')

    # Google OAuth (Authlib)
    from app.auth.oauth import init_oauth
    init_oauth(app)

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

    # Ban enforcement: if a logged-in user's account gets banned while they are
    # still in an active session, log them out on their very next request.
    @app.before_request
    def check_banned():
        from flask_login import logout_user
        from flask import redirect, url_for, flash
        if current_user.is_authenticated and not current_user.is_active_account:
            logout_user()
            flash('Your account has been suspended. Please contact support.', 'danger')
            return redirect(url_for('auth.login'))

    # Register blueprints here - they are like mini applications
    from app.auth.routes import auth_bp
    from app.user.routes import user_bp
    from app.swap.routes import swap_bp
    from app.notif_routes import notif_bp
    from app.messaging.routes import messaging_bp
    from app.scheduling.routes import scheduling_bp

    from app.admin.routes import admin_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(swap_bp)
    app.register_blueprint(notif_bp)
    app.register_blueprint(messaging_bp)
    app.register_blueprint(scheduling_bp)
    app.register_blueprint(admin_bp)

    # Exempt Google callback from CSRF — the redirect comes from Google, not our form
    csrf.exempt(auth_bp)

    @app.route('/')
    def index():
        return redirect(url_for('swap.home'))

    # Register global Jinja filter for IST time conversion
    @app.template_filter('to_ist')
    def to_ist(dt):
        if not dt:
            return ''
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(ZoneInfo('Asia/Kolkata'))

    # ── CLI: flask make-admin <email> ─────────────────────────────────────────
    # This is the ONLY way to promote a user to admin.
    # There is no web route for promotion — it must be run in the terminal.
    # Usage:  flask make-admin harshita@example.com
    import click
    @app.cli.command('make-admin')
    @click.argument('email')
    def make_admin(email):
        """Promote a user to admin by their email address."""
        from app.models import User
        user = User.query.filter_by(email=email).first()
        if not user:
            click.echo(f'❌ No user found with email: {email}')
            return
        if user.is_admin:
            click.echo(f'ℹ️  {email} is already an admin.')
            return
        user.is_admin = True
        db.session.commit()
        click.echo(f'✅ {email} is now an admin.')

    # Apply ProxyFix so url_for generates https:// behind Render's load balancer
    # x_proto=1: trust X-Forwarded-Proto header (sets https scheme)
    # x_host=1:  trust X-Forwarded-Host header (sets correct hostname)
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    return app
