from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    app.config['SECRET_KEY'] = 'your-secret-key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)

    # Import and register blueprints here
    from .auth.routes import auth_bp
    from .swap.routes import swap_bp
    

    app.register_blueprint(auth_bp)
    app.register_blueprint(swap_bp)

    return app
