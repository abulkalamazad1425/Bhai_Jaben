from pydantic import BaseModel, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class LocationSchema(BaseModel):
    latitude: float
    longitude: float
    address: Optional[str] = None

class RideCreateRequest(BaseModel):
    pickup: str
    drop: str
    pickup_coordinates: LocationSchema
    drop_coordinates: LocationSchema

class RideResponse(BaseModel):
    ride_id: str
    user_id: str
    driver_id: Optional[str] = None
    pickup: str
    drop: str
    status: str
    payment_status: str
    requested_at: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    fare: Optional[float] = None
    rating_by_user: Optional[float] = None
    rating_by_driver: Optional[float] = None
    cancel_reason: Optional[str] = None

class RideApplicationRequest(BaseModel):
    ride_id: str
    current_location: LocationSchema

class RideApplicationResponse(BaseModel):
    application_id: str
    ride_id: str
    driver_id: str
    driver_name: str
    driver_phone: str
    license: str
    vehicle_info: str
    current_location: LocationSchema
    applied_at: str
    estimated_arrival: Optional[str] = None

class DriverSelectionRequest(BaseModel):
    driver_id: str

class RideCancellationRequest(BaseModel):
    cancel_reason: str

class RideStatusUpdate(BaseModel):
    status: str
    start_time: Optional[str] = None
    end_time: Optional[str] = None

class RideRatingRequest(BaseModel):
    rating: float
    
    @validator('rating')
    def validate_rating(cls, v):
        if not 1.0 <= v <= 5.0:
            raise ValueError('Rating must be between 1.0 and 5.0')
        return v

# WebSocket message schemas
class WebSocketMessage(BaseModel):
    type: str
    data: dict
    timestamp: str

class RideUpdateMessage(BaseModel):
    ride_id: str
    status: str
    message: str
    data: Optional[dict] = None