#!/usr/bin/python3
"""
The prediction model for Gaine Africa
"""
from .base_model import BaseModel
from app import db

class Prediction(BaseModel):
    __tablename__ = "predictions"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    crop = db.Column(db.String(100), nullable=False)
    yield_estimate = db.Column(db.Float, nullable=False)
    market_price = db.Column(db.Float, nullable=False)
    prediction_date = db.Column(db.DateTime, default=db.func.current_timestamp())

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "crop": self.crop,
            "yield_estimate": self.yield_estimate,
            "market_price": self.market_price,
            "prediction_date": self.prediction_date,
        }
