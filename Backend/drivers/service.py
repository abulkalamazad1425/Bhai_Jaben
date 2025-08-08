from fastapi import HTTPException, status
from .schemas import DriverProfileResponse, DriverProfileUpdate
from typing import Dict

class DriverService:

    def __init__(self, supabase_client):
        self.supabase = supabase_client

    def view_driver_profile(self, current_user_id) -> DriverProfileResponse:
        try:
            # Get user data from users table
            user_response = self.supabase.table('users') \
                .select("*") \
                .eq('id', current_user_id) \
                .execute()

            if not user_response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            user_data = user_response.data[0]

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
                is_verified=user_data["is_verified"],
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

    def update_driver_profile(self, current_user_id, data: DriverProfileUpdate) -> Dict[str, str]:
        try:
            # First verify user exists and is a driver
            user_response = self.supabase.table('users') \
                .select("role") \
                .eq('id', current_user_id) \
                .execute()

            if not user_response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            if user_response.data[0]["role"] != "driver":
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="User is not a driver"
                )

            # Update user table fields if provided
            user_updates = {}
            if data.name is not None:
                user_updates["name"] = data.name
            if data.phone is not None:
                user_updates["phone"] = data.phone

            if user_updates:
                user_update_response = self.supabase.table('users') \
                    .update(user_updates) \
                    .eq('id', current_user_id) \
                    .execute()

                if not user_update_response.data:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Failed to update user information"
                    )

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