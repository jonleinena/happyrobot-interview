from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.fmcsa_service import fmcsa_service
from app.core.api_key_auth import get_api_key
from app.database import get_db
from app.schemas.carrier import CarrierVerificationResponse

router = APIRouter()


@router.get("/find", response_model=CarrierVerificationResponse)
async def verify_carrier(
    mc: str = Query(..., description="Motor Carrier number to verify"),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key)
):
    """
    Verify carrier eligibility using FMCSA API
    
    This endpoint verifies if a carrier is legitimate and eligible to work
    by checking their MC number against the FMCSA database.
    
    Returns:
        CarrierVerificationResponse with carrier details and verification status
    """
    if not mc:
        raise HTTPException(status_code=400, detail="MC number is required")
    
    # Call FMCSA service to verify carrier
    verification_result = await fmcsa_service.verify_carrier(mc)
    
    return verification_result 