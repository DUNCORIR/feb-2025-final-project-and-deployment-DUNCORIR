#!/usr/bin/python3
"""
Defines the BaseModel class for common database operations.
"""
from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash

class BaseModel(db.Model):
    """
    Base model class for common database operations.
    """

    __abstract__ = True  # Prevents SQLAlchemy from creating a table

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    def save(self):
        """Save the current instance to the database."""
        db.session.add(self)
        db.session.commit()

    def delete(self):
        """Delete the current instance from the database."""
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def get_by_id(cls, record_id):
        """Retrieve an instance by its ID."""
        return cls.query.get(record_id)

    @classmethod
    def get_all(cls):
        """Retrieve all instances of the model."""
        return cls.query.all()

    def update(self, **kwargs):
        """Update attributes of the instance and save changes."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.save()

    def to_dict(self):
        """Convert model instance to dictionary."""
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}
