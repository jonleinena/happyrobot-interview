from fastapi import APIRouter, Depends, HTTPException
from app.core.api_key_auth import get_api_key

router = APIRouter()


@router.get("/validate")
def validate_api_key(api_key: str = Depends(get_api_key)):
    """
    Validate API key endpoint
    
    This endpoint can be used to test if an API key is valid.
    """
    return {
        "status": "valid",
        "message": "API key is valid",
        "api_key_prefix": api_key[:8] + "..." if len(api_key) > 8 else api_key
    } 