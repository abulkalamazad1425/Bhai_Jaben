from pydantic import BaseModel
from typing import Optional, Dict, List
from datetime import datetime

class AdminUserResponse(BaseModel):
    user_id: str
    name: str
    email: str
    phone: str
    role: str
    is_active: bool
    created_at: str
    last_login: Optional[str] = None
    total_rides: int = 0
    total_spent: float = 0.0

class AdminDriverResponse(BaseModel):
    driver_id: str
    name: str
    email: str
    phone: str
    license_number: Optional[str] = None
    vehicle_info: Dict = {}
    status: str
    is_verified: bool
    is_active: bool
    created_at: str
    total_rides: int = 0
    total_earnings: float = 0.0
    average_rating: float = 0.0

class AdminRideResponse(BaseModel):
    ride_id: str
    user_id: str
    user_name: str
    driver_id: Optional[str] = None
    driver_name: Optional[str] = None
    pickup: str
    drop: str
    fare: Optional[float] = None
    distance: Optional[float] = None
    status: str
    payment_status: str
    payment_method: Optional[str] = None
    created_at: str
    completed_at: Optional[str] = None

class AdminPaymentResponse(BaseModel):
    payment_id: str
    ride_id: str
    user_id: Optional[str] = None
    driver_id: Optional[str] = None
    amount: float
    payment_method: str
    transaction_id: Optional[str] = None
    status: str
    created_at: str

class AdminDashboardResponse(BaseModel):
    total_users: int
    active_users: int
    total_drivers: int
    active_drivers: int
    online_drivers: int
    total_rides: int
    completed_rides: int
    ongoing_rides: int
    pending_rides: int
    today_rides: int
    total_revenue: float
    today_revenue: float
    average_ride_fare: float
    generated_at: str

class AdminStatsResponse(BaseModel):
    period: str
    stats: Dict

class UserDeactivateRequest(BaseModel):
    reason: Optional[str] = None

class DriverDeactivateRequest(BaseModel):
    reason: Optional[str] = None

# Pagination response models
class AdminUsersListResponse(BaseModel):
    users: List[AdminUserResponse]
    total_count: int
    page: int
    limit: int
    total_pages: int

class AdminDriversListResponse(BaseModel):
    drivers: List[AdminDriverResponse]
    total_count: int
    page: int
    limit: int
    total_pages: int

class AdminRidesListResponse(BaseModel):
    rides: List[AdminRideResponse]
    total_count: int
    page: int
    limit: int
    total_pages: int
    status_filter: Optional[str] = None

class AdminPaymentsListResponse(BaseModel):
    payments: List[AdminPaymentResponse]
    total_count: int
    page: int
    limit: int
    total_pages: int