#!/usr/bin/python3
"""
Initialize the database for the Gaine Africa application.

This script creates all database tables defined in the SQLAlchemy models.
"""

from dotenv import load_dotenv
from app import create_app, db


def initialize_database():
    """
    Initialize the database by creating all tables.
    """
    # Load environment variables from .env file
    load_dotenv()

    # Create the Flask application
    app = create_app()

    # Create all database tables within the application context
    with app.app_context():
        db.create_all()
        print("Database tables created successfully!")


if __name__ == '__main__':
    initialize_database()