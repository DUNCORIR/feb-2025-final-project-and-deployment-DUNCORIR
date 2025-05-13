#!/usr/bin/python3
"""
The script initializes the SQLAlchemy and Flask application.
"""
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_cors import CORS
from flask_migrate import Migrate
from config import Config
from flask_migrate import Migrate

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()

def create_app():
    """
    Create and configure the Flask application.

    Returns:
        Flask: The configured Flask application.
    """
    app = Flask(__name__)
    app.config.from_object("config.Config")
    app.secret_key = "maunyit"

    # Enable CORS for all routes with credentials support
    CORS(app, resources={
        r"/api/*": {
            "origins": "http://localhost:5173",
            "allow_headers": ["Authorization", "Content-Type"],
            "methods": ["GET", "POST", "PUT", "DELETE"],
            "supports_credentials": True
        }
    })

    # Initialize the database with the app
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)

    # Import models within the function to avoid circular imports
    from app.models import BaseModel, User, Record, Prediction, MarketData

    # Register the main routes blueprint
    from .routes import main_routes
    app.register_blueprint(main_routes)

    return app
