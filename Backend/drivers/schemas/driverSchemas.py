from pydantic import BaseModel
from typing import Optional

class DriverProfileUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    license: Optional[str] = None
    vehicle_info: Optional[str] = None

class DriverProfileOut(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    role: str
    license: str
    vehicle_info: str


class AvailabilityUpdate(BaseModel):
    is_available: bool

class RideActionResponse(BaseModel):
    message: str
