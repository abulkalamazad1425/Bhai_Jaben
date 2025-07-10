from pydantic import BaseModel

class PaymentRequest(BaseModel):
    name: str
    email: str
    phone: str
    amount: float
