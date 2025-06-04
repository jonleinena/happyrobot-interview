from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from app.database import Base


class Load(Base):
    __tablename__ = "loads"

    id = Column(Integer, primary_key=True, index=True)
    load_id = Column(String, unique=True, index=True, nullable=False)  # Unique identifier
    origin = Column(String, nullable=False)  # Starting location
    destination = Column(String, nullable=False)  # Delivery location
    pickup_datetime = Column(DateTime, nullable=False)  # Date and time for pickup
    delivery_datetime = Column(DateTime, nullable=False)  # Date and time for delivery
    equipment_type = Column(String, nullable=False)  # Type of equipment needed
    loadboard_rate = Column(Float, nullable=False)  # Listed rate for the load
    notes = Column(Text)  # Additional information
    weight = Column(Float)  # Load weight in lbs
    commodity_type = Column(String)  # Type of goods
    num_of_pieces = Column(Integer)  # Number of items
    miles = Column(Float)  # Distance to travel
    dimensions = Column(String)  # Size measurements
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now()) 