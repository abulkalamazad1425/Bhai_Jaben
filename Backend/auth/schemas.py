from pydantic import BaseModel, EmailStr

class UserSignup(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone: str
    role: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str