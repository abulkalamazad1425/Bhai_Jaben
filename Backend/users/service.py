from fastapi import HTTPException, status, Request
from .schemas import UserProfile
from typing import Dict, Optional

class UserService:

    def __init__(self, supabase_client):
        self.supabase = supabase_client


    def view_profile(self, current_user_id) -> UserProfile:
        try:
            response = self.supabase.table('users') \
                .select("*") \
                .eq('id', current_user_id) \
                .execute()

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Profile not found"
                )

            user_data = response.data[0]  
            return UserProfile(
                id=user_data["id"],          
                name=user_data["name"],
                email=user_data["email"],
                phone=user_data["phone"],
                role=user_data["role"],
                is_verified=user_data["is_verified"],
                created_at=user_data["created_at"]
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    # New method for driver module to get user data
    def get_user_data(self, user_id) -> Dict:
        try:
            response = self.supabase.table('users') \
                .select("*") \
                .eq('id', user_id) \
                .execute()

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            return response.data[0]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    # Method to update user data (for driver module)
    def update_user_data(self, user_id, updates: Dict) -> Dict:
        try:
            if not updates:
                return {"message": "No updates provided"}

            response = self.supabase.table('users') \
                .update(updates) \
                .eq('id', user_id) \
                .execute()

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to update user information"
                )

            return {"message": "User data updated successfully"}
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    # Method to verify user role
    def verify_user_role(self, user_id, expected_role: str) -> bool:
        try:
            response = self.supabase.table('users') \
                .select("role") \
                .eq('id', user_id) \
                .execute()

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found"
                )

            return response.data[0]["role"] == expected_role
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )