from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from decimal import Decimal

@dataclass
class Ride:
    ride_id: str
    user_id: str
    pickup: str
    drop: str
    status: str
    payment_status: str
    requested_at: datetime
    driver_id: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    fare: Optional[Decimal] = None
    rating_by_user: Optional[float] = None
    rating_by_driver: Optional[float] = None
    cancel_reason: Optional[str] = None

@dataclass
class RideApplication:
    application_id: str
    ride_id: str
    driver_id: str
    locations: str
    applied_at: datetime

@dataclass
class Location:
    latitude: float
    longitude: float
    address: Optional[str] = None