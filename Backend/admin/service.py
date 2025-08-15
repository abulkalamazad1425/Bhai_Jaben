from fastapi import HTTPException, status
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import uuid

from users.service import UserService
from drivers.service import DriverService
from rides.service import RideService
from payments.service import PaymentService
from .schemas import (
    AdminUserResponse, AdminDriverResponse, AdminRideResponse, 
    AdminPaymentResponse, AdminStatsResponse, AdminDashboardResponse,
    UserDeactivateRequest, DriverDeactivateRequest
)

class AdminService:
    def __init__(self, supabase_client):
        self.user_service = UserService(supabase_client)
        self.driver_service = DriverService(supabase_client)
        self.ride_service = RideService(supabase_client)
        self.payment_service = PaymentService(supabase_client)
        self.supabase = supabase_client
    
    def verify_admin_access(self, user_id: str) -> bool:
        """Verify if user has admin access"""
        try:
            user_data = self.user_service.get_user_data(user_id)
            return user_data.get("role") == "admin"
        except Exception:
            return False
    
    # User Management Methods
    def get_all_users(self, current_admin_id: str, page: int = 1, limit: int = 50) -> Dict:
        """Get all users with pagination"""
        try:
            if not self.verify_admin_access(current_admin_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required"
                )
            
            # Get users from user service
            users_data = self.user_service.get_all_users_admin(page=page, limit=limit)
            
            # Transform data for admin response
            admin_users = []
            for user in users_data.get("users", []):
                admin_user = AdminUserResponse(
                    user_id=user["user_id"],
                    name=user["name"],
                    email=user["email"],
                    phone=user["phone"],
                    role=user.get("role", "user"),
                    is_active=user.get("is_active", True),
                    created_at=user["created_at"],
                    last_login=user.get("last_login"),
                    total_rides=user.get("total_rides", 0),
                    total_spent=user.get("total_spent", 0.0)
                )
                admin_users.append(admin_user)
            
            return {
                "users": admin_users,
                "total_count": users_data.get("total_count", 0),
                "page": page,
                "limit": limit,
                "total_pages": (users_data.get("total_count", 0) + limit - 1) // limit
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching users: {str(e)}"
            )
    
    def deactivate_user(self, current_admin_id: str, user_id: str, reason: Optional[str] = None) -> Dict[str, str]:
        """Deactivate a user account"""
        try:
            if not self.verify_admin_access(current_admin_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required"
                )
            
            # Check if user exists and is not admin
            user_data = self.user_service.get_user_data(user_id)
            if user_data.get("role") == "admin":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Cannot deactivate admin users"
                )
            
            # Deactivate user through user service
            result = self.user_service.deactivate_user_admin(user_id, current_admin_id, reason)
            
            return {
                "message": "User deactivated successfully",
                "user_id": user_id,
                "deactivated_by": current_admin_id,
                "reason": reason,
                "deactivated_at": datetime.now().isoformat()
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deactivating user: {str(e)}"
            )
    
    def activate_user(self, current_admin_id: str, user_id: str) -> Dict[str, str]:
        """Activate a user account"""
        try:
            if not self.verify_admin_access(current_admin_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required"
                )
            
            # Activate user through user service
            result = self.user_service.activate_user_admin(user_id, current_admin_id)
            
            return {
                "message": "User activated successfully",
                "user_id": user_id,
                "activated_by": current_admin_id,
                "activated_at": datetime.now().isoformat()
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error activating user: {str(e)}"
            )
    
    # Driver Management Methods
    def get_all_drivers(self, current_admin_id: str, page: int = 1, limit: int = 50) -> Dict:
        """Get all drivers with pagination"""
        try:
            if not self.verify_admin_access(current_admin_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required"
                )
            
            # Get drivers from driver service
            drivers_data = self.driver_service.get_all_drivers_admin(page=page, limit=limit)
            
            # Transform data for admin response
            admin_drivers = []
            for driver in drivers_data.get("drivers", []):
                admin_driver = AdminDriverResponse(
                    driver_id=driver["driver_id"],
                    name=driver["name"],
                    email=driver["email"],
                    phone=driver["phone"],
                    license_number=driver.get("license_number"),
                    vehicle_info=driver.get("vehicle_info", {}),
                    status=driver.get("status", "offline"),
                    is_verified=driver.get("is_verified", False),
                    is_active=driver.get("is_active", True),
                    created_at=driver["created_at"],
                    total_rides=driver.get("total_rides", 0),
                    total_earnings=driver.get("total_earnings", 0.0),
                    average_rating=driver.get("average_rating", 0.0)
                )
                admin_drivers.append(admin_driver)
            
            return {
                "drivers": admin_drivers,
                "total_count": drivers_data.get("total_count", 0),
                "page": page,
                "limit": limit,
                "total_pages": (drivers_data.get("total_count", 0) + limit - 1) // limit
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching drivers: {str(e)}"
            )
    
    def deactivate_driver(self, current_admin_id: str, driver_id: str, reason: Optional[str] = None) -> Dict[str, str]:
        """Deactivate a driver account"""
        try:
            if not self.verify_admin_access(current_admin_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required"
                )
            
            # Deactivate driver through driver service
            result = self.driver_service.deactivate_driver_admin(driver_id, current_admin_id, reason)
            
            return {
                "message": "Driver deactivated successfully",
                "driver_id": driver_id,
                "deactivated_by": current_admin_id,
                "reason": reason,
                "deactivated_at": datetime.now().isoformat()
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deactivating driver: {str(e)}"
            )
    
    def activate_driver(self, current_admin_id: str, driver_id: str) -> Dict[str, str]:
        """Activate a driver account"""
        try:
            if not self.verify_admin_access(current_admin_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required"
                )
            
            # Activate driver through driver service
            result = self.driver_service.activate_driver_admin(driver_id, current_admin_id)
            
            return {
                "message": "Driver activated successfully",
                "driver_id": driver_id,
                "activated_by": current_admin_id,
                "activated_at": datetime.now().isoformat()
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error activating driver: {str(e)}"
            )
    
    # Ride Management Methods
    def get_all_rides(self, current_admin_id: str, status_filter: Optional[str] = None, 
                     page: int = 1, limit: int = 50) -> Dict:
        """Get all rides with optional status filter"""
        try:
            if not self.verify_admin_access(current_admin_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required"
                )
            
            # Get rides from ride service
            rides_data = self.ride_service.get_all_rides_admin(
                status_filter=status_filter, 
                page=page, 
                limit=limit
            )
            
            # Transform data for admin response
            admin_rides = []
            for ride in rides_data.get("rides", []):
                # Get payment info for this ride
                try:
                    payment_info = self.payment_service.get_payment_by_ride_id_admin(ride["ride_id"])
                except:
                    payment_info = None
                
                admin_ride = AdminRideResponse(
                    ride_id=ride["ride_id"],
                    user_id=ride["user_id"],
                    user_name=ride.get("user_name", "Unknown"),
                    driver_id=ride.get("driver_id"),
                    driver_name=ride.get("driver_name"),
                    pickup=ride["pickup"],
                    drop=ride["drop"],
                    fare=ride.get("fare"),
                    distance=ride.get("distance"),
                    status=ride["status"],
                    payment_status=ride.get("payment_status", "pending"),
                    payment_method=payment_info.get("payment_method") if payment_info else None,
                    created_at=ride["created_at"],
                    completed_at=ride.get("completed_at")
                )
                admin_rides.append(admin_ride)
            
            return {
                "rides": admin_rides,
                "total_count": rides_data.get("total_count", 0),
                "page": page,
                "limit": limit,
                "total_pages": (rides_data.get("total_count", 0) + limit - 1) // limit,
                "status_filter": status_filter
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching rides: {str(e)}"
            )
    
    # Payment Management Methods
    def get_all_payments(self, current_admin_id: str, page: int = 1, limit: int = 50) -> Dict:
        """Get all payments with pagination"""
        try:
            if not self.verify_admin_access(current_admin_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required"
                )
            
            # Get payments from payment service
            payments_data = self.payment_service.get_all_payments_admin(page=page, limit=limit)
            
            # Transform data for admin response
            admin_payments = []
            for payment in payments_data.get("payments", []):
                admin_payment = AdminPaymentResponse(
                    payment_id=payment["id"],
                    ride_id=payment["ride_id"],
                    user_id=payment.get("user_id"),
                    driver_id=payment.get("driver_id"),
                    amount=payment["amount"],
                    payment_method=payment["payment_method"],
                    transaction_id=payment.get("transaction_id"),
                    status=payment["status"],
                    created_at=payment["created_at"]
                )
                admin_payments.append(admin_payment)
            
            return {
                "payments": admin_payments,
                "total_count": payments_data.get("total_count", 0),
                "page": page,
                "limit": limit,
                "total_pages": (payments_data.get("total_count", 0) + limit - 1) // limit
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching payments: {str(e)}"
            )
    
    # Dashboard and Analytics Methods
    def get_dashboard_stats(self, current_admin_id: str) -> AdminDashboardResponse:
        """Get admin dashboard statistics"""
        try:
            if not self.verify_admin_access(current_admin_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required"
                )
            
            # Get stats from all services
            user_stats = self.user_service.get_user_stats_admin()
            driver_stats = self.driver_service.get_driver_stats_admin()
            ride_stats = self.ride_service.get_ride_stats_admin()
            payment_stats = self.payment_service.get_payment_stats_admin()
            
            # Calculate today's stats
            today = datetime.now().date()
            today_rides = self.ride_service.get_rides_by_date_admin(today)
            today_revenue = self.payment_service.get_revenue_by_date_admin(today)
            
            return AdminDashboardResponse(
                total_users=user_stats.get("total_users", 0),
                active_users=user_stats.get("active_users", 0),
                total_drivers=driver_stats.get("total_drivers", 0),
                active_drivers=driver_stats.get("active_drivers", 0),
                online_drivers=driver_stats.get("online_drivers", 0),
                total_rides=ride_stats.get("total_rides", 0),
                completed_rides=ride_stats.get("completed_rides", 0),
                ongoing_rides=ride_stats.get("ongoing_rides", 0),
                pending_rides=ride_stats.get("pending_rides", 0),
                today_rides=len(today_rides),
                total_revenue=payment_stats.get("total_revenue", 0.0),
                today_revenue=today_revenue,
                average_ride_fare=ride_stats.get("average_fare", 0.0),
                generated_at=datetime.now().isoformat()
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error generating dashboard stats: {str(e)}"
            )
    
    def get_revenue_analytics(self, current_admin_id: str, start_date: str, end_date: str) -> Dict:
        """Get revenue analytics for date range"""
        try:
            if not self.verify_admin_access(current_admin_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required"
                )
            
            # Get revenue data from payment service
            revenue_data = self.payment_service.get_revenue_analytics_admin(start_date, end_date)
            
            return revenue_data
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching revenue analytics: {str(e)}"
            )
    
    def get_ride_details_admin(self, current_admin_id: str, ride_id: str) -> Dict:
        """Get detailed ride information for admin"""
        try:
            if not self.verify_admin_access(current_admin_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required"
                )
            
            # Get ride details
            ride = self.ride_service.get_ride_by_id(ride_id)
            if not ride:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Ride not found"
                )
            
            # Get payment info
            payment_info = self.payment_service.get_payment_by_ride_id_admin(ride_id)
            
            # Get user and driver info
            user_info = self.user_service.get_user_data(ride['user_id'])
            driver_info = None
            if ride.get('driver_id'):
                driver_info = self.driver_service.get_driver_data(ride['driver_id'])
            
            return {
                "ride": ride,
                "payment": payment_info,
                "user": user_info,
                "driver": driver_info
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching ride details: {str(e)}"
            )
    
    def get_payment_details_admin(self, current_admin_id: str, payment_id: str) -> Dict:
        """Get detailed payment information for admin"""
        try:
            if not self.verify_admin_access(current_admin_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required"
                )
            
            # Get payment details
            payment = self.payment_service.get_payment_by_id(payment_id)
            if not payment:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Payment not found"
                )
            
            # Get related ride info
            ride_info = self.ride_service.get_ride_by_id(payment['ride_id'])
            
            return {
                "payment": payment,
                "ride": ride_info
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching payment details: {str(e)}"
            )
    
    def get_user_analytics(self, current_admin_id: str, period: str) -> Dict:
        """Get user analytics for specified period"""
        try:
            if not self.verify_admin_access(current_admin_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required"
                )
            
            # Calculate date range based on period
            end_date = datetime.now()
            if period == "day":
                start_date = end_date - timedelta(days=1)
            elif period == "week":
                start_date = end_date - timedelta(days=7)
            elif period == "month":
                start_date = end_date - timedelta(days=30)
            elif period == "year":
                start_date = end_date - timedelta(days=365)
            else:
                start_date = end_date - timedelta(days=30)
            
            # Get user registration data for the period
            response = self.supabase.table('users')\
                .select('created_at')\
                .gte('created_at', start_date.isoformat())\
                .lte('created_at', end_date.isoformat())\
                .execute()
            
            # Process data for analytics
            daily_registrations = {}
            for user in response.data:
                date = user['created_at'][:10]
                if date not in daily_registrations:
                    daily_registrations[date] = 0
                daily_registrations[date] += 1
            
            return {
                "period": period,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "daily_registrations": daily_registrations,
                "total_new_users": len(response.data)
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching user analytics: {str(e)}"
            )
    
    def get_ride_analytics(self, current_admin_id: str, period: str) -> Dict:
        """Get ride analytics for specified period"""
        try:
            if not self.verify_admin_access(current_admin_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Admin access required"
                )
            
            # Calculate date range based on period
            end_date = datetime.now()
            if period == "day":
                start_date = end_date - timedelta(days=1)
            elif period == "week":
                start_date = end_date - timedelta(days=7)
            elif period == "month":
                start_date = end_date - timedelta(days=30)
            elif period == "year":
                start_date = end_date - timedelta(days=365)
            else:
                start_date = end_date - timedelta(days=30)
            
            # Get ride data for the period
            response = self.supabase.table('rides')\
                .select('created_at, status, fare')\
                .gte('created_at', start_date.isoformat())\
                .lte('created_at', end_date.isoformat())\
                .execute()
            
            # Process data for analytics
            daily_rides = {}
            status_breakdown = {}
            total_fare = 0
            
            for ride in response.data:
                date = ride['created_at'][:10]
                
                # Daily rides count
                if date not in daily_rides:
                    daily_rides[date] = 0
                daily_rides[date] += 1
                
                # Status breakdown
                status = ride['status']
                if status not in status_breakdown:
                    status_breakdown[status] = 0
                status_breakdown[status] += 1
                
                # Total fare
                if ride.get('fare'):
                    total_fare += ride['fare']
            
            return {
                "period": period,
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat(),
                "daily_rides": daily_rides,
                "status_breakdown": status_breakdown,
                "total_rides": len(response.data),
                "total_fare": total_fare
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching ride analytics: {str(e)}"
            )