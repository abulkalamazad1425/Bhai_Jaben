from fastapi import HTTPException
from .schemas import UserProfile

class UserService:

    def __init__(self, supabase_client):
        self.supabase = supabase_client


    def get_profile(self, user_id):
        result = self.supabase.table("users").select("*").eq("id", user_id).single().execute()

        if result.data is None:
            raise HTTPException(status_code=404, detail="Profile not found")

        return result.data