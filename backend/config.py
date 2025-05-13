#!/usr/bin/python3

"""
Configuration settings for the Gaine Africa Flask application.

This module defines the configuration variables required for the application,
such as the database connection URI.
"""

from dotenv import load_dotenv
import os


# Load environment variables from .env file
load_dotenv()


class Config:
    """
    Configuration class for the Flask application.

    Attributes:
        SQLALCHEMY_DATABASE_URI (str): The URI for the MySQL database.
        SQLALCHEMY_TRACK_MODIFICATIONS (bool): Disable modification tracking.
    """

    # Database configuration
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', 'mysql+pymysql://root:maunyit@localhost/gaine_africa')
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT Configuration (Fixing KeyError issue)
    SECRET_KEY = os.getenv("SECRET_KEY", "maunyit")  # Change this to a strong key
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "maunyit")  # Used for signing JWTs
    JWT_TOKEN_LOCATION = ["headers"]  # Ensure JWT is passed in headers
    JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour expiration
    JWT_REFRESH_TOKEN_EXPIRES = 86400  # 1 day expiration

    # Debugging: Print the DATABASE_URI
    print(f"Database URI: {SQLALCHEMY_DATABASE_URI}")
