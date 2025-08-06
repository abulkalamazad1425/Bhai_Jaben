from fastapi import APIRouter, Depends, HTTPException
from typing import Any, Dict
from uuid import UUID

from .database_config import DatabaseConfig
from .schemas import DriverProfileOut, DriverProfileUpdate
from .services import DriverService
from auth.services.login_service import LoginService

router = APIRouter(prefix='/driver', tags=['Driver'])

# Initialize services
database_client = DatabaseConfig().get_client()
driver_service = RegisterService(database_client)
login_service = LoginService(database_client)

@router.get("/profile", response_model=DriverProfileOut)
def view_driver_profile(current_user_id: UUID = Depends(login_service.get_current_user)) -> DriverProfileOut:
    return driver_service.get_driver_profile(current_user_id)

@router.put("/profile")
def update_driver_profile(
    data: DriverProfileUpdate,
    current_user_id: UUID = Depends(login_service.get_current_user)
) -> Dict[str, str]:
    return driver_service.update_driver_profile(current_user_id, data)
