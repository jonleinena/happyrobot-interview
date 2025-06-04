from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.api_key_auth import get_api_key
from app.models.call_log import CallLog
from app.schemas.carrier import CallOutcome, CallOutcomeResponse


router = APIRouter()


@router.post("/log", response_model=CallOutcomeResponse)
def log_call_outcome(
    call_outcome: CallOutcome,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key),
    request: Request = None
):
    """
    Log the outcome of a call with a carrier
    
    This endpoint allows the AI to record the complete outcome of a call
    including negotiation details, sentiment, and final result.
    """
    # Validate that required fields are provided
    if not call_outcome.happyrobot_run_id:
        print(call_outcome)
        print(request.body)
        raise HTTPException(status_code=400, detail="happyrobot_run_id is required")
    
    if not call_outcome.call_outcome_classification:
        raise HTTPException(status_code=400, detail="call_outcome_classification is required")
    
    if not call_outcome.carrier_sentiment_classification:
        raise HTTPException(status_code=400, detail="carrier_sentiment_classification is required")
    
    # Check if call log already exists for this happyrobot_run_id
    existing_call = db.query(CallLog).filter(CallLog.happyrobot_run_id == call_outcome.happyrobot_run_id).first()
    if existing_call:
        raise HTTPException(status_code=409, detail="Call log already exists for this happyrobot_run_id")
    
    # Create call log record
    db_call_log = CallLog(
        happyrobot_run_id=call_outcome.happyrobot_run_id,
        mc_number=call_outcome.mc_number,
        searched_load_id=call_outcome.load_id,
        agreed_rate=call_outcome.agreed_rate,
        call_outcome_classification=call_outcome.call_outcome_classification,
        carrier_sentiment_classification=call_outcome.carrier_sentiment_classification,
        fmcsa_verified_eligible=call_outcome.fmcsa_verified_eligible == "ACTIVE",
        initial_carrier_offer=float(call_outcome.initial_carrier_offer) if call_outcome.initial_carrier_offer else None,
        negotiation_rounds=int(call_outcome.negotiation_rounds) if call_outcome.negotiation_rounds else 0,
        raw_extracted_data_json=call_outcome.raw_extracted_data
    )
    
    db.add(db_call_log)
    db.commit()
    db.refresh(db_call_log)
    
    return CallOutcomeResponse(
        status=201,
        message="Call outcome logged successfully",
        call_log_id=db_call_log.id
    ) 