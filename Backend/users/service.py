from fastapi import HTTPException
from .supabase_config import supabase
from .schemas import UserProfile


def get_profile(user_id):
    result = supabase.table("users").select("*").eq("id", user_id).single().execute()

    if result.data is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    return result.data