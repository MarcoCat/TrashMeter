from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from dotenv import load_dotenv
import os

# Initialize extensions
db = SQLAlchemy()
mail = Mail()

def create_app():
    """Construct the core application."""
    app = Flask(__name__)
    load_dotenv()  # Load environment variables from .env file

    # Configurations from environment variables
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SECURITY_PASSWORD_SALT'] = os.getenv('SECURITY_PASSWORD_SALT')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL').replace('postgres://', 'postgresql://')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
    app.config['MAIL_PORT'] = os.getenv('MAIL_PORT')
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS')
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER', os.getenv('MAIL_USERNAME'))

    db.init_app(app)
    mail.init_app(app)

    with app.app_context():
        # Import parts of our application
        from . import routes, models

        # Create tables for our models
        db.create_all()

        return app
