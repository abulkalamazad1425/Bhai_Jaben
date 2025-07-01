from pydantic import BaseModel, EmailStr

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