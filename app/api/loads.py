from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from datetime import datetime, date

from app.database import get_db
from app.core.api_key_auth import get_api_key
from app.models.load import Load as LoadModel
from app.schemas.load import Load, LoadSearchParams

router = APIRouter()


@router.get("/", response_model=List[Load])
def search_loads(
    origin_city: Optional[str] = Query(None, description="Filter by origin city"),
    destination_city: Optional[str] = Query(None, description="Filter by destination city"),
    equipment_type: Optional[str] = Query(None, description="Filter by equipment type"),
    pickup_date: Optional[str] = Query(None, description="Filter by pickup date (YYYY-MM-DD)"),
    max_weight: Optional[float] = Query(None, description="Maximum weight filter"),
    min_rate: Optional[float] = Query(None, description="Minimum rate filter"),
    max_rate: Optional[float] = Query(None, description="Maximum rate filter"),
    limit: int = Query(10, description="Maximum number of results to return", le=100),
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key)
):
    """
    Search for loads based on criteria
    
    This endpoint allows the AI to search for loads that match specific criteria
    provided by the carrier during the call.
    """
    query = db.query(LoadModel)
    
    # Apply filters
    filters = []
    
    if origin_city:
        filters.append(LoadModel.origin.ilike(f"%{origin_city}%"))
    
    if destination_city:
        filters.append(LoadModel.destination.ilike(f"%{destination_city}%"))
    
    if equipment_type:
        filters.append(LoadModel.equipment_type.ilike(f"%{equipment_type}%"))
    
    if pickup_date:
        try:
            pickup_date_obj = datetime.strptime(pickup_date, "%Y-%m-%d").date()
            filters.append(LoadModel.pickup_datetime >= pickup_date_obj)
            # Also filter for same day or next day
            next_day = datetime.combine(pickup_date_obj, datetime.min.time()).replace(
                day=pickup_date_obj.day + 1
            ) if pickup_date_obj.day < 28 else datetime.combine(pickup_date_obj, datetime.min.time()).replace(
                month=pickup_date_obj.month + 1, day=1
            )
            filters.append(LoadModel.pickup_datetime < next_day)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid pickup_date format. Use YYYY-MM-DD")
    
    if max_weight and max_weight > 0:
        filters.append(LoadModel.weight <= max_weight)
    
    if min_rate and min_rate > 0:
        filters.append(LoadModel.loadboard_rate >= min_rate)
    
    if max_rate and max_rate > 0:
        filters.append(LoadModel.loadboard_rate <= max_rate)
    
    # Apply all filters
    if filters:
        query = query.filter(and_(*filters))
    
    # Order by pickup date and rate
    query = query.order_by(LoadModel.pickup_datetime, LoadModel.loadboard_rate.desc())
    
    # Apply limit
    loads = query.limit(limit).all()
    
    return loads


@router.get("/{load_id}", response_model=Load)
def get_load_details(
    load_id: str,
    db: Session = Depends(get_db),
    api_key: str = Depends(get_api_key)
):
    """
    Get specific load details by load_id
    
    This endpoint allows the AI to get detailed information about a specific load
    identified by its load_id.
    """
    load = db.query(LoadModel).filter(LoadModel.load_id == load_id).first()
    
    if not load:
        raise HTTPException(status_code=404, detail="Load not found")
    
    return load 