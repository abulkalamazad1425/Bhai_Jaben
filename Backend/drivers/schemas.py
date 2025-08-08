from typing import Optional
from uuid import UUID
from pydantic import BaseModel

class DriverProfileResponse(BaseModel):
    user_id: UUID
    name: str
    email: str
    phone: str
    license: str
    vehicle_info: str
    is_verified: bool
    is_approved: bool

class DriverProfileUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    license: Optional[str] = None
    vehicle_info: Optional[str] = None

class DriverProfileCreate(BaseModel):
    license: str
    vehicle_info: str