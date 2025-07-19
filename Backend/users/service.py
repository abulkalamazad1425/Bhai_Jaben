from fastapi import HTTPException, status, Request
from .schemas import UserProfile

class UserService:

    def __init__(self, supabase_client):
        self.supabase = supabase_client


    def view_profile(self, current_user_id)->UserProfile:
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