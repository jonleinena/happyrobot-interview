from datetime import datetime
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field


class CarrierVerificationResponse(BaseModel):
    carrier_id: str = Field(..., description="The MC or DOT number")
    carrier_name: str = Field(..., description="Carrier name from FMCSA")
    status: str = Field(..., description="Verification status: ACTIVE, FAIL, SUSPENDED, INACTIVE, UNREGISTERED")
    dot_number: Optional[str] = Field(None, description="DOT number from FMCSA")
    mc_number: Optional[str] = Field(None, description="MC number")


class CarrierOfferLog(BaseModel):
    load_id: str = Field(..., description="Load ID being discussed")
    mc_number: str = Field(..., description="Carrier MC number")
    carrier_offer: float = Field(..., description="Amount offered by carrier")
    notes: Optional[str] = Field(None, description="Additional notes about the offer")


class CarrierOfferResponse(BaseModel):
    status: int = Field(201, description="HTTP status code")
    message: str = Field("Offer logged successfully", description="Response message")


class CallOutcome(BaseModel):
    happyrobot_run_id: str = Field(..., description="Unique call ID from HappyRobot")
    mc_number: Optional[str] = Field(None, description="Carrier MC number")
    load_id: Optional[str] = Field(None, description="Load ID discussed")
    agreed_rate: Optional[float] = Field(None, description="Final agreed rate")
    call_outcome_classification: str = Field(..., description="Call outcome classification")
    carrier_sentiment_classification: str = Field(..., description="Carrier sentiment classification")
    fmcsa_verified_eligible: Optional[str] = Field(None, description="Whether carrier passed verification")
    initial_carrier_offer: Optional[str] = Field(None, description="First offer made")
    negotiation_rounds: Optional[str] = Field(0, description="Number of negotiation rounds")
    raw_extracted_data: Optional[Dict[str, Any]] = Field(None, description="Full extracted data from call")


class CallOutcomeResponse(BaseModel):
    status: int = Field(201, description="HTTP status code")
    message: str = Field("Call outcome logged successfully", description="Response message")
    call_log_id: int = Field(..., description="ID of the created call log record") 