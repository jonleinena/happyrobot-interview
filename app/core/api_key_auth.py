from fastapi import HTTPException, status, Depends
from fastapi.security.api_key import APIKeyHeader
from app.config import settings

# API Key authentication
api_key_header = APIKeyHeader(name="Authorization", auto_error=False)


async def get_api_key(api_key: str = Depends(api_key_header)):
    """
    Validate API key for endpoint access
    
    Args:
        api_key: API key from header
        
    Returns:
        str: Valid API key
        
    Raises:
        HTTPException: If API key is invalid or missing
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key is required. Add API-Key header.",
        )
    
    # Get the expected API key from settings and strip whitespace
    expected_api_key = settings.API_KEY.strip() if settings.API_KEY else None
    
    if not expected_api_key:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="API Key not configured on server",
        )
    
    # Strip whitespace from incoming API key as well
    clean_api_key = api_key.replace("ApiKey", "").strip()
    
    if clean_api_key != expected_api_key:
        print(f"Invalid API Key: '{clean_api_key}' != '{expected_api_key}'")
        print(f"Lengths: {len(clean_api_key)} vs {len(expected_api_key)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API Key",
        )
    
    return api_key 