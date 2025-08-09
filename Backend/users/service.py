from fastapi import HTTPException, status, Request
from .schemas import UserProfile, UserProfileUpdate
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
                created_at=user_data["created_at"]
            )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    def update_profile(self, current_user_id: str, update_data: UserProfileUpdate) -> Dict[str, str]:
        try:
            # Check if user exists
            existing_user = self.get_user_data(current_user_id)
            
            # Prepare update data - only include fields that are being updated
            updates = {}
            
            if update_data.name is not None:
                updates["name"] = update_data.name
            
            if update_data.email is not None:
                # Check if email is already taken by another user
                if update_data.email != existing_user["email"]:
                    email_check = self.supabase.table('users') \
                        .select("id") \
                        .eq('email', update_data.email) \
                        .neq('id', current_user_id) \
                        .execute()
                    
                    if email_check.data:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Email is already taken by another user"
                        )
                
                updates["email"] = update_data.email
            
            if update_data.phone is not None:
                # Check if phone is already taken by another user
                if update_data.phone != existing_user["phone"]:
                    phone_check = self.supabase.table('users') \
                        .select("id") \
                        .eq('phone', update_data.phone) \
                        .neq('id', current_user_id) \
                        .execute()
                    
                    if phone_check.data:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Phone number is already taken by another user"
                        )
                
                updates["phone"] = update_data.phone
            
            # If no updates provided
            if not updates:
                return {"message": "No changes to update"}
            
            # Perform the update
            response = self.supabase.table('users') \
                .update(updates) \
                .eq('id', current_user_id) \
                .execute()

            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to update profile"
                )

            return {"message": "Profile updated successfully"}
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    # Method for other modules to get user data
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
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    # Method to update user data (for other modules like driver service)
    def update_user_data(self, user_id, updates: Dict) -> Dict:
        try:
            if not updates:
                return {"message": "No updates provided"}

            # Validate email uniqueness if email is being updated
            if "email" in updates:
                existing_user = self.get_user_data(user_id)
                if updates["email"] != existing_user["email"]:
                    email_check = self.supabase.table('users') \
                        .select("id") \
                        .eq('email', updates["email"]) \
                        .neq('id', user_id) \
                        .execute()
                    
                    if email_check.data:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Email is already taken by another user"
                        )

            # Validate phone uniqueness if phone is being updated
            if "phone" in updates:
                existing_user = self.get_user_data(user_id)
                if updates["phone"] != existing_user["phone"]:
                    phone_check = self.supabase.table('users') \
                        .select("id") \
                        .eq('phone', updates["phone"]) \
                        .neq('id', user_id) \
                        .execute()
                    
                    if phone_check.data:
                        raise HTTPException(
                            status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Phone number is already taken by another user"
                        )

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
        except HTTPException:
            raise
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
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )

    # Method to get user profile by user_id (for internal use)
    def get_user_profile_by_id(self, user_id: str) -> UserProfile:
        try:
            user_data = self.get_user_data(user_id)
            return UserProfile(
                id=user_data["id"],          
                name=user_data["name"],
                email=user_data["email"],
                phone=user_data["phone"],
                role=user_data["role"],
                created_at=user_data["created_at"]
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )