from fastapi import APIRouter, Depends, HTTPException
from typing import Any, Dict
from .supabase_config import supabase
from .service import UserService
from .schemas import UserProfile
from auth.services.login_service import LoginService

router = APIRouter(prefix='/user', tags=['User'])

user_service = UserService(supabase)
login_service = LoginService(supabase)

@router.get("/profile", response_model=UserProfile)
def view_profile(current_user_id: int = Depends(login_service.get_current_user)) -> UserProfile:
    return user_service.view_profile(current_user_id)
    
        
'''
def get_profile(user_id) -> UserProfile:
    """
    Get the current user's profile.
    
    Requires valid JWT authentication token.
    """
    try:
        
        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="User ID not found in token"
            )
        
        profile = user_service.get_profile(user_id)
        if not profile:
            raise HTTPException(
                status_code=404,
                detail="User profile not found"
            )
            
        return profile
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving profile: {str(e)}"
        )
'''
