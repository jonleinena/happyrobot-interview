from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.api_key_auth import get_api_key
from app.models.call_log import CarrierOffer
from app.schemas.carrier import CarrierOfferLog, CarrierOfferResponse

router = APIRouter()


@router.post("/log", response_model=CarrierOfferResponse)
def log_carrier_offer(
    offer: CarrierOfferLog,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key)
):
    """
    Log a carrier's offer during negotiation
    
    This endpoint allows the AI to record offers made by carriers during
    the negotiation process. It helps track the negotiation history.
    """
    # Validate that load_id and mc_number are provided
    if not offer.load_id:
        raise HTTPException(status_code=400, detail="load_id is required")
    
    if not offer.mc_number:
        raise HTTPException(status_code=400, detail="mc_number is required")
    
    if offer.carrier_offer <= 0:
        raise HTTPException(status_code=400, detail="carrier_offer must be greater than 0")
    
    # Create carrier offer record
    db_offer = CarrierOffer(
        load_id=offer.load_id,
        mc_number=offer.mc_number,
        carrier_offer=offer.carrier_offer,
        notes=offer.notes
    )
    
    db.add(db_offer)
    db.commit()
    db.refresh(db_offer)
    
    return CarrierOfferResponse(
        status=201,
        message="Offer logged successfully"
    ) 