import httpx
import logging
from typing import Optional, Dict, Any
from app.schemas.carrier import CarrierVerificationResponse
from app.config import settings

logger = logging.getLogger(__name__)


class FMCSAService:
    """Service to interact with FMCSA API for carrier verification"""
    
    def __init__(self):
        self.base_url = "https://mobile.fmcsa.dot.gov/qc/services/carriers"
        self.timeout = 30.0
    
    async def verify_carrier(self, mc_number: str) -> CarrierVerificationResponse:
        """
        Verify carrier eligibility using FMCSA API
        
        Args:
            mc_number: Motor Carrier number to verify
            
        Returns:
            CarrierVerificationResponse with verification details
        """
        try:
            # Clean the MC number (remove 'MC' prefix if present)
            clean_mc = mc_number.upper().replace('MC', '').strip()
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # FMCSA API endpoint for carrier lookup
                # Based on the documentation, the API key is required to be passed in the query string
                url = f"{self.base_url}/{clean_mc}?webKey={settings.FMCSA_API_KEY.strip()}"
                
                headers = {
                    "User-Agent": "HappyRobot-CarrierVerification/1.0",
                    "Accept": "application/json",
                }
                
                logger.info(f"Calling FMCSA API for MC: {clean_mc}")
                response = await client.get(url, headers=headers)
                
                if response.status_code == 200:
                    data = response.json()
                    return self._process_fmcsa_response(data, clean_mc)
                elif response.status_code == 404:
                    return CarrierVerificationResponse(
                        carrier_id=clean_mc,
                        carrier_name="UNKNOWN",
                        status="UNREGISTERED",
                        mc_number=clean_mc
                    )
                else:
                    print("else")
                    logger.error(f"FMCSA API error: {response.status_code} - {response.text}")
                    return CarrierVerificationResponse(
                        carrier_id=clean_mc,
                        carrier_name="UNKNOWN",
                        status="FAIL",
                        mc_number=clean_mc
                    )
                    
        except httpx.TimeoutException:
            logger.error(f"FMCSA API timeout for MC: {clean_mc}")
            return CarrierVerificationResponse(
                carrier_id=clean_mc,
                carrier_name="UNKNOWN",
                status="FAIL",
                mc_number=clean_mc
            )
        except Exception as e:
            logger.error(f"Error verifying carrier {clean_mc}: {str(e)}")
            return CarrierVerificationResponse(
                carrier_id=clean_mc,
                carrier_name="UNKNOWN",
                status="FAIL",
                mc_number=clean_mc
            )
    
    def _process_fmcsa_response(self, data: Dict[str, Any], mc_number: str) -> CarrierVerificationResponse:
        """
        Process FMCSA API response and determine carrier status
        
        Args:
            data: Response data from FMCSA API
            mc_number: Original MC number
            
        Returns:
            CarrierVerificationResponse with processed data
        """
        try:
            # Extract carrier information from nested structure
            carrier = data['content']['carrier']
            
            carrier_name = carrier.get('legalName', 'UNKNOWN')
            dot_number = str(carrier.get('dotNumber', ''))
            
            # Determine status based on FMCSA data
            status_code = carrier.get('statusCode', '').upper()
            allowed_to_operate = carrier.get('allowedToOperate', '').upper()
            safety_rating = carrier.get('safetyRating', '').upper()
            
            # Check various status indicators
            if status_code == 'A' and allowed_to_operate == 'Y':
                # Active carrier, check safety rating
                if safety_rating in ['S', 'SATISFACTORY', '', 'NONE']:  # S = Satisfactory
                    status = "ACTIVE"
                elif safety_rating in ['U', 'UNSATISFACTORY']:
                    status = "FAIL"  # Unsatisfactory safety rating
                else:
                    status = "ACTIVE"  # Default to active if safety rating is unclear
            elif status_code in ['S', 'SUSPENDED']:
                status = "SUSPENDED"
            elif status_code in ['I', 'INACTIVE']:
                status = "INACTIVE"
            elif allowed_to_operate == 'N':
                status = "SUSPENDED"
            else:
                status = "FAIL"  # Unknown or problematic status
            
            return CarrierVerificationResponse(
                carrier_id=dot_number or mc_number,
                carrier_name=carrier_name,
                status=status,
                dot_number=dot_number,
                mc_number=mc_number
            )
            
        except Exception as e:
            logger.error(f"Error processing FMCSA response: {str(e)}")
            return CarrierVerificationResponse(
                carrier_id=mc_number,
                carrier_name="UNKNOWN",
                status="FAIL",
                mc_number=mc_number
            )


# Singleton instance
fmcsa_service = FMCSAService() 