from fastapi import HTTPException
from postgrest.exceptions import APIError
from ..supabase_client import supabase
from ..schemas.driverSchemas import DriverProfileOut, DriverProfileUpdate

class DriverService:
    def __init__(self):
        self.supabase = supabase

    def get_driver_profile(self, user_id: str) -> DriverProfileOut:
        try:
            # Try fetching user
            try:
                user_resp = (
                    self.supabase
                    .table("users")
                    .select("*")
                    .eq("id", user_id)
                    .single()
                    .execute()
                )
                if not user_resp.data:
                    raise APIError("User not found")    
                user_resp = user_resp.data
            except APIError as e:
                raise HTTPException(status_code=404, detail="User not found")

            # Try fetching driver profile
            try:
                profile_resp = (
                    self.supabase
                    .table("driver_profiles")
                    .select("*")
                    .eq("user_id", user_id)
                    .single()
                    .execute()
                )
                if not profile_resp.data:
                    raise APIError("Driver profile not found")
                profile_resp = profile_resp.data
            except APIError as e:
                raise HTTPException(status_code=404, detail="Driver profile not found")

            return DriverProfileOut(
                id=user_resp["id"],
                name=user_resp["name"],
                email=user_resp["email"],
                phone=user_resp["phone"],
                role=user_resp["role"],
                license=profile_resp["license"],
                vehicle_info=profile_resp["vehicle_info"]
            )

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
        
    def update_driver_profile(self, user_id: str, updates: DriverProfileUpdate) -> DriverProfileOut:
        try:
            user_updates = {}
            profile_updates = {}

            if updates.name is not None:
                user_updates["name"] = updates.name
            if updates.email is not None:
                user_updates["email"] = updates.email
            if updates.phone is not None:
                user_updates["phone"] = updates.phone
            if updates.role is not None:
                user_updates["role"] = updates.role

            if updates.license is not None:
                profile_updates["license"] = updates.license
            if updates.vehicle_info is not None:
                profile_updates["vehicle_info"] = updates.vehicle_info

            # Update users table
            if user_updates:
                user_resp = self.supabase.table("users").update(user_updates).eq("id", user_id).execute()
                if user_resp.data is None:
                    raise HTTPException(status_code=400, detail=f"Failed to update user data: {user_resp.error.message}")

            # Update driver_profiles table
            if profile_updates:
                profile_resp = self.supabase.table("driver_profiles").update(profile_updates).eq("user_id", user_id).execute()
                if profile_resp.data is None:
                    raise HTTPException(status_code=400, detail=f"Failed to update driver profile: {profile_resp.error.message}")

            # Return updated profile
            return self.get_driver_profile(user_id)

        except HTTPException:
            raise
        except APIError as e:
            raise HTTPException(status_code=400, detail=f"Database error: {str(e)}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
