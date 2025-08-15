from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from .service import AdminService
from .schemas import (
    AdminUsersListResponse, AdminDriversListResponse, AdminRidesListResponse,
    AdminPaymentsListResponse, AdminDashboardResponse, UserDeactivateRequest,
    DriverDeactivateRequest
)
from auth.services.login_service import LoginService
from .database_config import DatabaseConfig

router = APIRouter(prefix='/api/admin', tags=['Admin'])

# Initialize services
database_client = DatabaseConfig().get_client()
admin_service = AdminService(database_client)
login_service = LoginService(database_client)

# User Management Routes
@router.get("/users", response_model=AdminUsersListResponse)
def get_all_users(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    current_admin_id: str = Depends(login_service.get_current_user)
):
    """Get all users - Admin only"""
    return admin_service.get_all_users(current_admin_id, page=page, limit=limit)

@router.patch("/users/{user_id}/deactivate")
def deactivate_user(
    user_id: str,
    request: UserDeactivateRequest,
    current_admin_id: str = Depends(login_service.get_current_user)
):
    """Deactivate a user - Admin only"""
    return admin_service.deactivate_user(
        current_admin_id, 
        user_id, 
        reason=request.reason
    )

@router.patch("/users/{user_id}/activate")
def activate_user(
    user_id: str,
    current_admin_id: str = Depends(login_service.get_current_user)
):
    """Activate a user - Admin only"""
    return admin_service.activate_user(current_admin_id, user_id)

# Driver Management Routes
@router.get("/drivers", response_model=AdminDriversListResponse)
def get_all_drivers(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    current_admin_id: str = Depends(login_service.get_current_user)
):
    """Get all drivers - Admin only"""
    return admin_service.get_all_drivers(current_admin_id, page=page, limit=limit)

@router.patch("/drivers/{driver_id}/deactivate")
def deactivate_driver(
    driver_id: str,
    request: DriverDeactivateRequest,
    current_admin_id: str = Depends(login_service.get_current_user)
):
    """Deactivate a driver - Admin only"""
    return admin_service.deactivate_driver(
        current_admin_id, 
        driver_id, 
        reason=request.reason
    )

@router.patch("/drivers/{driver_id}/activate")
def activate_driver(
    driver_id: str,
    current_admin_id: str = Depends(login_service.get_current_user)
):
    """Activate a driver - Admin only"""
    return admin_service.activate_driver(current_admin_id, driver_id)

# Ride Management Routes
@router.get("/rides", response_model=AdminRidesListResponse)
def get_all_rides(
    status: Optional[str] = Query(None, description="Filter by ride status"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    current_admin_id: str = Depends(login_service.get_current_user)
):
    """Get all rides with optional status filter - Admin only"""
    return admin_service.get_all_rides(
        current_admin_id, 
        status_filter=status, 
        page=page, 
        limit=limit
    )

@router.get("/rides/{ride_id}/details")
def get_ride_details(
    ride_id: str,
    current_admin_id: str = Depends(login_service.get_current_user)
):
    """Get detailed ride information - Admin only"""
    return admin_service.get_ride_details_admin(current_admin_id, ride_id)

# Payment Management Routes
@router.get("/payments", response_model=AdminPaymentsListResponse)
def get_all_payments(
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=100),
    current_admin_id: str = Depends(login_service.get_current_user)
):
    """Get all payments - Admin only"""
    return admin_service.get_all_payments(current_admin_id, page=page, limit=limit)

@router.get("/payments/{payment_id}/details")
def get_payment_details(
    payment_id: str,
    current_admin_id: str = Depends(login_service.get_current_user)
):
    """Get detailed payment information - Admin only"""
    return admin_service.get_payment_details_admin(current_admin_id, payment_id)

# Dashboard and Analytics Routes
@router.get("/dashboard", response_model=AdminDashboardResponse)
def get_dashboard_stats(
    current_admin_id: str = Depends(login_service.get_current_user)
):
    """Get admin dashboard statistics - Admin only"""
    return admin_service.get_dashboard_stats(current_admin_id)

@router.get("/analytics/revenue")
def get_revenue_analytics(
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    current_admin_id: str = Depends(login_service.get_current_user)
):
    """Get revenue analytics for date range - Admin only"""
    return admin_service.get_revenue_analytics(current_admin_id, start_date, end_date)

@router.get("/analytics/users")
def get_user_analytics(
    period: str = Query("month", description="Period: day, week, month, year"),
    current_admin_id: str = Depends(login_service.get_current_user)
):
    """Get user analytics - Admin only"""
    return admin_service.get_user_analytics(current_admin_id, period)

@router.get("/analytics/rides")
def get_ride_analytics(
    period: str = Query("month", description="Period: day, week, month, year"),
    current_admin_id: str = Depends(login_service.get_current_user)
):
    """Get ride analytics - Admin only"""
    return admin_service.get_ride_analytics(current_admin_id, period)