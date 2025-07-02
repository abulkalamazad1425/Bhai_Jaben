from fastapi import APIRouter, Depends, HTTPException
from typing import Any, Dict
from .supabase_config import supabase
from .service import UserService
from .schemas import UserProfile
from auth.utils import jwt_auth

router = APIRouter(prefix='/user', tags=['User'])

user_service = UserService(supabase)

@router.get(
    "/profile", 
    response_model=UserProfile,
    responses={
        401: {"description": "Invalid or missing token"},
        404: {"description": "User profile not found"},
        500: {"description": "Internal server error"}
    }
)
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
def get_profile(user: Dict[str, Any] = Depends(jwt_auth.get_current_user)) -> UserProfile:
    """
    Get the current user's profile.
    
    Requires valid JWT authentication token.
    """
    try:
        user_id = user.get('sub') or user.get('id')  # 'sub' is standard JWT claim for subject/user ID
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
