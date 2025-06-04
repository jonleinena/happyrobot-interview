from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.sql import func
from app.database import Base


class CallLog(Base):
    __tablename__ = "call_logs"

    id = Column(Integer, primary_key=True, index=True)
    happyrobot_run_id = Column(String, unique=True, index=True)  # ID from HappyRobot platform
    mc_number = Column(String, index=True)  # Motor carrier number
    called_at = Column(DateTime, default=func.now())  # When the call occurred
    fmcsa_verified_eligible = Column(Boolean, default=False)  # Whether carrier passed FMCSA verification
    searched_load_id = Column(String)  # Load ID that was discussed
    initial_carrier_offer = Column(Float)  # First offer made by carrier
    negotiation_rounds = Column(Integer, default=0)  # Number of back-and-forth negotiations
    agreed_rate = Column(Float)  # Final agreed upon rate
    call_outcome_classification = Column(String)  # e.g., "Booked", "Rejected - Price", "No Interest"
    carrier_sentiment_classification = Column(String)  # e.g., "Positive", "Negative", "Neutral"
    raw_extracted_data_json = Column(JSON)  # Full extracted data from HappyRobot
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class CarrierOffer(Base):
    __tablename__ = "carrier_offers"

    id = Column(Integer, primary_key=True, index=True)
    load_id = Column(String, nullable=False, index=True)
    mc_number = Column(String, nullable=False, index=True)
    carrier_offer = Column(Float, nullable=False)
    notes = Column(Text)
    offered_at = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now()) 