from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class DriverProfileResponse(BaseModel):
    user_id: str
    name: str
    email: str
    phone: str
    role: str
    created_at: str
    license: str
    vehicle_info: str
    is_approved: bool

class DriverProfileUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    license: Optional[str] = None
    vehicle_info: Optional[str] = None

class DriverProfileCreate(BaseModel):
    license: str
    vehicle_info: str