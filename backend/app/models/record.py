#!/usr/bin/python3
"""
Defines the Record model for the Gaine Africa application.
"""

from .base_model import BaseModel
from app import db


class Record(BaseModel):
    """
    Represents a farming record for a user.
    """

    __tablename__ = 'records'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    crop = db.Column(db.String(100), nullable=False)  # Type of crop being recorded

    # Costs involved in farming
    planting = db.Column(db.Float, nullable=False, default=0.0)
    weeding = db.Column(db.Float, nullable=False, default=0.0)
    harvesting = db.Column(db.Float, nullable=False, default=0.0)
    storage = db.Column(db.Float, nullable=False, default=0.0)

    sales = db.Column(db.Float, nullable=False, default=0.0)  # Total revenue from sales

    @property
    def profit_or_loss(self):
        """Calculate profit/loss dynamically (not stored in DB)."""
        total_expenses = self.planting + self.weeding + self.harvesting + self.storage
        return self.sales - total_expenses
    
    def to_dict(self):
        """Convert record to dictionary including profit/loss."""
        return {
            "id": self.id,
            "crop": self.crop,
            "planting": self.planting,
            "weeding": self.weeding,
            "harvesting": self.harvesting,
            "storage": self.storage,
            "sales": self.sales,
            "profit_or_loss": self.calculate_profit_or_loss()  # Include in output
        }

    def save(self):
        """Save the record with calculated profit/loss (if needed)."""
        super().save()  # Call the parent class's save method
