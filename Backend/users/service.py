from fastapi import HTTPException, status, Request
from .schemas import UserProfile

class UserService:

    def __init__(self, supabase_client):
        self.supabase = supabase_client


    def view_profile(self, current_user)->UserProfile:
        try:
                # Set auth token for this request
            self.supabase.postgrest.auth(current_user.access_token)
                
                # Get profile for current user
            response = self.supabase.table('users') \
                .select("*") \
                .eq('user_id', current_user.id) \
                .execute()
                    
            if not response.data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Profile not found"
                )
                    
            return response.data[0]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )