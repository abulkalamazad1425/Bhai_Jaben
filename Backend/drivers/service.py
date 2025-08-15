from fastapi import HTTPException, status
from .schemas import DriverProfileResponse, DriverProfileUpdate
from users.service import UserService
from typing import Dict, Optional
from datetime import datetime

class DriverService:

    def __init__(self, supabase_client):
        self.supabase = supabase_client
        self.user_service = UserService(supabase_client)

    def view_driver_profile(self, current_user_id) -> DriverProfileResponse:
        try:
            # Get user data from users service
            user_data = self.user_service.get_user_data(current_user_id)

            # Check if user is a driver
            if user_data["role"] != "driver":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User is not a driver"
                )

            # Get driver profile data from driver_profiles table
            driver_response = self.supabase.table('driver_profiles') \
                .select("*") \
                .eq('user_id', current_user_id) \
                .execute()

            if not driver_response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Driver profile not found"
                )

            driver_data = driver_response.data[0]

            return DriverProfileResponse(
                user_id=user_data["id"],
                name=user_data["name"],
                email=user_data["email"],
                phone=user_data["phone"],
                role=user_data["role"],
                created_at=user_data["created_at"],
                license=driver_data["license"],
                vehicle_info=driver_data["vehicle_info"],
                is_approved=driver_data["is_approved"]
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    # Method for rides service to get driver profile
    def get_driver_profile_for_ride(self, driver_id: str) -> Dict:
        """Get driver profile data for ride applications"""
        try:
            # Get user data from users service
            user_data = self.user_service.get_user_data(driver_id)

            # Verify user is a driver
            if user_data["role"] != "driver":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="User is not a driver"
                )

            # Get driver profile data
            driver_response = self.supabase.table('driver_profiles') \
                .select("*") \
                .eq('user_id', driver_id) \
                .execute()

            if not driver_response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Driver profile not found"
                )

            driver_data = driver_response.data[0]

            return {
                "name": user_data["name"],
                "phone": user_data["phone"],
                "license": driver_data["license"],
                "vehicle_info": driver_data["vehicle_info"],
                "is_approved": driver_data["is_approved"]
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    def update_driver_profile(self, current_user_id, data: DriverProfileUpdate) -> Dict[str, str]:
        try:
            # Verify user exists and is a driver using user service
            if not self.user_service.verify_user_role(current_user_id, "driver"):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User is not a driver"
                )

            # Update user table fields if provided (through user service)
            user_updates = {}
            if data.name is not None:
                user_updates["name"] = data.name
            if data.phone is not None:
                user_updates["phone"] = data.phone

            if user_updates:
                self.user_service.update_user_data(current_user_id, user_updates)

            # Update driver profile fields if provided
            driver_updates = {}
            if data.license is not None:
                driver_updates["license"] = data.license
            if data.vehicle_info is not None:
                driver_updates["vehicle_info"] = data.vehicle_info

            if driver_updates:
                driver_update_response = self.supabase.table('driver_profiles') \
                    .update(driver_updates) \
                    .eq('user_id', current_user_id) \
                    .execute()

                if not driver_update_response.data:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Failed to update driver profile"
                    )

            return {"message": "Driver profile updated successfully"}

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    def get_all_drivers_admin(self, page: int = 1, limit: int = 50) -> Dict:
        """Get all drivers for admin with pagination"""
        try:
            offset = (page - 1) * limit
            
            # Get total count
            count_response = self.supabase.table('drivers').select('*', count='exact').execute()
            total_count = count_response.count
            
            # Get drivers with pagination
            response = self.supabase.table('drivers')\
                .select('*')\
                .range(offset, offset + limit - 1)\
                .order('created_at', desc=True)\
                .execute()
            
            drivers = []
            for driver in response.data:
                # Get driver stats
                driver_stats = self._get_driver_stats(driver['driver_id'])
                
                driver_data = {
                    "driver_id": driver['driver_id'],
                    "name": driver['name'],
                    "email": driver['email'],
                    "phone": driver['phone'],
                    "license_number": driver.get('license_number'),
                    "vehicle_info": driver.get('vehicle_info', {}),
                    "status": driver.get('status', 'offline'),
                    "is_verified": driver.get('is_verified', False),
                    "is_active": driver.get('is_active', True),
                    "created_at": driver['created_at'],
                    "total_rides": driver_stats.get('total_rides', 0),
                    "total_earnings": driver_stats.get('total_earnings', 0.0),
                    "average_rating": driver_stats.get('average_rating', 0.0)
                }
                drivers.append(driver_data)
            
            return {
                "drivers": drivers,
                "total_count": total_count
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching drivers: {str(e)}"
            )
    
    def _get_driver_stats(self, driver_id: str) -> Dict:
        """Get statistics for a driver"""
        try:
            # Get completed rides
            rides_response = self.supabase.table('rides')\
                .select('*')\
                .eq('driver_id', driver_id)\
                .eq('status', 'completed')\
                .execute()
            
            total_rides = len(rides_response.data)
            
            # Get total earnings from payments
            ride_ids = [ride['ride_id'] for ride in rides_response.data]
            total_earnings = 0.0
            
            if ride_ids:
                payments_response = self.supabase.table('payments')\
                    .select('amount')\
                    .in_('ride_id', ride_ids)\
                    .eq('status', 'completed')\
                    .execute()
                
                total_earnings = sum(payment['amount'] for payment in payments_response.data)
            
            # Get average rating
            ratings_response = self.supabase.table('ride_ratings')\
                .select('rating')\
                .eq('rated_user_id', driver_id)\
                .eq('rater_type', 'user')\
                .execute()
            
            average_rating = 0.0
            if ratings_response.data:
                average_rating = sum(rating['rating'] for rating in ratings_response.data) / len(ratings_response.data)
            
            return {
                "total_rides": total_rides,
                "total_earnings": total_earnings,
                "average_rating": round(average_rating, 2)
            }
            
        except Exception:
            return {
                "total_rides": 0,
                "total_earnings": 0.0,
                "average_rating": 0.0
            }
    
    def deactivate_driver_admin(self, driver_id: str, admin_id: str, reason: Optional[str] = None) -> Dict:
        """Deactivate driver by admin"""
        try:
            # Update driver status
            response = self.supabase.table('drivers')\
                .update({
                    'is_active': False,
                    'status': 'offline',
                    'deactivated_by': admin_id,
                    'deactivated_at': datetime.now().isoformat(),
                    'deactivation_reason': reason,
                    'updated_at': datetime.now().isoformat()
                })\
                .eq('driver_id', driver_id)\
                .execute()
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Driver not found"
                )
            
            return {"message": "Driver deactivated successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error deactivating driver: {str(e)}"
            )
    
    def activate_driver_admin(self, driver_id: str, admin_id: str) -> Dict:
        """Activate driver by admin"""
        try:
            # Update driver status
            response = self.supabase.table('drivers')\
                .update({
                    'is_active': True,
                    'activated_by': admin_id,
                    'activated_at': datetime.now().isoformat(),
                    'deactivation_reason': None,
                    'updated_at': datetime.now().isoformat()
                })\
                .eq('driver_id', driver_id)\
                .execute()
            
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Driver not found"
                )
            
            return {"message": "Driver activated successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error activating driver: {str(e)}"
            )
    
    def get_driver_stats_admin(self) -> Dict:
        """Get driver statistics for admin dashboard"""
        try:
            # Total drivers
            total_response = self.supabase.table('drivers').select('*', count='exact').execute()
            total_drivers = total_response.count
            
            # Active drivers
            active_response = self.supabase.table('drivers')\
                .select('*', count='exact')\
                .eq('is_active', True)\
                .execute()
            active_drivers = active_response.count
            
            # Online drivers
            online_response = self.supabase.table('drivers')\
                .select('*', count='exact')\
                .eq('status', 'online')\
                .eq('is_active', True)\
                .execute()
            online_drivers = online_response.count
            
            # Verified drivers
            verified_response = self.supabase.table('drivers')\
                .select('*', count='exact')\
                .eq('is_verified', True)\
                .execute()
            verified_drivers = verified_response.count
            
            return {
                "total_drivers": total_drivers,
                "active_drivers": active_drivers,
                "online_drivers": online_drivers,
                "verified_drivers": verified_drivers
            }
            
        except Exception as e:
            return {
                "total_drivers": 0,
                "active_drivers": 0,
                "online_drivers": 0,
                "verified_drivers": 0
            }