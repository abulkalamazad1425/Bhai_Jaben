from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime

class UserProfile(BaseModel):
    id: UUID
    name: str
    email: str
    phone: str
    role: str  
    is_verified: bool
    created_at: datetime
