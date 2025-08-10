from pydantic import BaseModel, validator
from typing import List, Optional, Union
from decimal import Decimal
from datetime import datetime

class PaymentBase(BaseModel):
    ride_id: str
    amount: Decimal
    payment_method: str
    
    @validator('payment_method')
    def validate_payment_method(cls, v):
        if v not in ['cash', 'online']:
            raise ValueError('Payment method must be either "cash" or "online"')
        return v

    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('Amount must be greater than 0')
        return v

class CashPaymentRequest(BaseModel):
    ride_id: str

class OnlinePaymentRequest(BaseModel):
    ride_id: str
    success_url: Optional[str] = None
    fail_url: Optional[str] = None
    cancel_url: Optional[str] = None

class PaymentResponse(BaseModel):
    id: str
    ride_id: str
    amount: float
    payment_method: str
    transaction_id: Optional[str] = None
    status: str
    created_at: str
    updated_at: Optional[str] = None

class OnlinePaymentInitResponse(BaseModel):
    payment_url: str
    session_key: str
    # payment_id: str
    
class SSLCommerzRequest(BaseModel):
    store_id: str
    store_passwd: str
    total_amount: Decimal
    currency: str
    tran_id: str
    success_url: str
    fail_url: str
    cancel_url: str
    cus_name: str
    cus_email: str
    cus_phone: str
    cus_add1: str
    cus_city: str
    cus_country: str
    shipping_method: str
    product_name: str
    product_category: str
    product_profile: str

class SSLCommerzResponse(BaseModel):
    status: str
    failedreason: Optional[str] = None
    sessionkey: Optional[str] = None
    gw: Optional[str] = None
    redirectGatewayURL: Optional[str] = None
    directPaymentURLBank: Optional[str] = None
    redirectGatewayURLFailed: Optional[str] = None
    GatewayPageURL: Optional[str] = None
    storeBanner: Optional[str] = None
    store_logo: Optional[str] = None
    desc: Optional[List] = None
    is_direct_pay_enable: Optional[str] = None

class PaymentCallbackRequest(BaseModel):
    val_id: str
    store_id: str
    store_passwd: str
    v: str = "1"
    format: str = "json"

# Response schemas for different payment outcomes
class PaymentSuccessResponse(BaseModel):
    message: str
    ride_id: str
    payment_id: str
    transaction_id: str
    amount: str
    payment_method: str
    status: str

class PaymentFailureResponse(BaseModel):
    message: str
    ride_id: Optional[str] = None
    payment_id: Optional[str] = None
    error: str
    status: str

class PaymentCancelResponse(BaseModel):
    message: str
    ride_id: Optional[str] = None
    payment_id: Optional[str] = None
    status: str
