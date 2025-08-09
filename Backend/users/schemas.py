from typing import Optional
from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime

class UserProfile(BaseModel):
    id: UUID
    name: str
    email: str
    phone: str
    role: str  
    created_at: datetime

class UserProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
