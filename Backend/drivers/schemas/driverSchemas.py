from pydantic import BaseModel

class DriverProfileOut(BaseModel):
    id: str
    name: str
    email: str
    phone: str
    role: str
    license: str
    vehicle_info: str
