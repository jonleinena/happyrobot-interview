from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class LoadBase(BaseModel):
    load_id: str = Field(..., description="Unique identifier for the load")
    origin: str = Field(..., description="Starting location")
    destination: str = Field(..., description="Delivery location")
    pickup_datetime: datetime = Field(..., description="Date and time for pickup")
    delivery_datetime: datetime = Field(..., description="Date and time for delivery")
    equipment_type: str = Field(..., description="Type of equipment needed")
    loadboard_rate: float = Field(..., description="Listed rate for the load")
    notes: Optional[str] = Field(None, description="Additional information")
    weight: Optional[float] = Field(None, description="Load weight in lbs")
    commodity_type: Optional[str] = Field(None, description="Type of goods")
    num_of_pieces: Optional[int] = Field(None, description="Number of items")
    miles: Optional[float] = Field(None, description="Distance to travel")
    dimensions: Optional[str] = Field(None, description="Size measurements")


class LoadCreate(LoadBase):
    pass


class LoadUpdate(BaseModel):
    origin: Optional[str] = None
    destination: Optional[str] = None
    pickup_datetime: Optional[datetime] = None
    delivery_datetime: Optional[datetime] = None
    equipment_type: Optional[str] = None
    loadboard_rate: Optional[float] = None
    notes: Optional[str] = None
    weight: Optional[float] = None
    commodity_type: Optional[str] = None
    num_of_pieces: Optional[int] = None
    miles: Optional[float] = None
    dimensions: Optional[str] = None


class Load(LoadBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LoadSearchParams(BaseModel):
    origin_city: Optional[str] = Field(None, description="Filter by origin city")
    destination_city: Optional[str] = Field(None, description="Filter by destination city")
    equipment_type: Optional[str] = Field(None, description="Filter by equipment type")
    pickup_date: Optional[str] = Field(None, description="Filter by pickup date (YYYY-MM-DD)")
    max_weight: Optional[float] = Field(None, description="Maximum weight filter")
    min_rate: Optional[float] = Field(None, description="Minimum rate filter")
    max_rate: Optional[float] = Field(None, description="Maximum rate filter") 