from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime

class UserSignup(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: str
    role: str


class DriverSignup(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: str
    role: str
    license: str
    vehicle_info: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserId(BaseModel):
    id: UUID

class UserBase(BaseModel):
    id: UUID
    email: str
    created_at: datetime

class AuthResponse(BaseModel):
    user: UserBase
    access_token: str
    refresh_token: str

class TokenData(BaseModel):
    access_token: str
    refresh_token: str