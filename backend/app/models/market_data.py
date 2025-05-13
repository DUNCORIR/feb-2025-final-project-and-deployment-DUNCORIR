#!/usr/bin/python3
"""
Defines the MarketData model for the Gaine Africa application.
"""

from .base_model import BaseModel
from app import db


class MarketData(BaseModel):
    """
    Represents market data for crops.
    """

    __tablename__ = 'market_data'

    id = db.Column(db.Integer, primary_key=True)
    crop_type = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False)
    data_timestamp = db.Column(db.TIMESTAMP, default=db.func.current_timestamp())
    source = db.Column(db.String(255))
