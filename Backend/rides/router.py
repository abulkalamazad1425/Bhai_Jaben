from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict
from .service import RideService
from .schemas import RideCreateRequest, RideResponse, RideApplicationRequest, RideApplicationResponse, DriverSelectionRequest, RideCancellationRequest
from auth.services.login_service import LoginService
from .database_config import DatabaseConfig

router = APIRouter(prefix='/rides', tags=['Rides'])

# Initialize services
database_client = DatabaseConfig().get_client()
ride_service = RideService(database_client)
login_service = LoginService(database_client)

@router.post("/create", response_model=RideResponse)
async def create_ride(
    ride_data: RideCreateRequest,
    current_user_id: str = Depends(login_service.get_current_user)
) -> RideResponse:
    return await ride_service.create_ride(current_user_id, ride_data)

@router.get("/pending", response_model=List[RideResponse])
def get_pending_rides(
    current_user_id: str = Depends(login_service.get_current_user)
) -> List[RideResponse]:
    return ride_service.get_pending_rides(current_user_id)

@router.post("/apply")
async def apply_for_ride(
    application_data: RideApplicationRequest,
    current_user_id: str = Depends(login_service.get_current_user)
) -> Dict[str, str]:
    return await ride_service.apply_for_ride(current_user_id, application_data)

@router.get("/{ride_id}/applications", response_model=List[RideApplicationResponse])
def get_ride_applications(
    ride_id: str,
    current_user_id: str = Depends(login_service.get_current_user)
) -> List[RideApplicationResponse]:
    return ride_service.get_ride_applications(current_user_id, ride_id)

@router.post("/{ride_id}/select-driver")
async def select_driver(
    ride_id: str,
    selection: DriverSelectionRequest,
    current_user_id: str = Depends(login_service.get_current_user)
) -> Dict[str, str]:
    return await ride_service.select_driver(current_user_id, ride_id, selection.driver_id)

@router.post("/{ride_id}/start")
async def start_ride(
    ride_id: str,
    current_user_id: str = Depends(login_service.get_current_user)
) -> Dict[str, str]:
    return await ride_service.start_ride(current_user_id, ride_id)

@router.post("/{ride_id}/complete")
async def complete_ride(
    ride_id: str,
    current_user_id: str = Depends(login_service.get_current_user)
) -> Dict[str, str]:
    return await ride_service.complete_ride(current_user_id, ride_id)

@router.post("/{ride_id}/cancel")
async def cancel_ride(
    ride_id: str,
    cancellation: RideCancellationRequest,
    current_user_id: str = Depends(login_service.get_current_user)
) -> Dict[str, str]:
    return await ride_service.cancel_ride(current_user_id, ride_id, cancellation.cancel_reason)