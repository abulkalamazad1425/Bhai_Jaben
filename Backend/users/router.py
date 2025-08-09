from fastapi import APIRouter, Depends, HTTPException
from typing import Dict
from .service import UserService
from .schemas import UserProfile, UserProfileUpdate
from auth.services.login_service import LoginService
from .database_config import DatabaseConfig

router = APIRouter(prefix='/users', tags=['Users'])

database_client = DatabaseConfig().get_client()
user_service = UserService(database_client)
login_service = LoginService(database_client)

@router.get("/profile", response_model=UserProfile)
def view_profile(current_user_id: str = Depends(login_service.get_current_user)) -> UserProfile:
    return user_service.view_profile(current_user_id)

@router.put("/profile")
def update_profile(update_data: UserProfileUpdate,current_user_id: str = Depends(login_service.get_current_user)) -> Dict[str, str]:
    return user_service.update_profile(current_user_id, update_data)

@router.get("/profile/{user_id}", response_model=UserProfile)
def get_user_profile_by_id(user_id: str,current_user_id: str = Depends(login_service.get_current_user)) -> UserProfile:
    
    return user_service.get_user_profile_by_id(user_id)
