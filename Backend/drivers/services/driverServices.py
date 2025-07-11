from fastapi import HTTPException
from postgrest.exceptions import APIError
from ..supabase_client import supabase
from ..schemas.driverSchemas import DriverProfileOut

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
