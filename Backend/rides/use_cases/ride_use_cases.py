from typing import List, Dict, Optional
from ..repositories.ride_repository import RideRepository, RideApplicationRepository
from ..domain.services import FareCalculationService, LocationService
from ..schemas import RideCreateRequest, RideResponse, RideApplicationRequest
from users.service import UserService
from fastapi import HTTPException, status
import uuid
from datetime import datetime
import json

class CreateRideUseCase:
    def __init__(self, ride_repo: RideRepository, user_service: UserService):
        self.ride_repo = ride_repo
        self.user_service = user_service
        self.fare_service = FareCalculationService()
    
    def execute(self, user_id: str, request: RideCreateRequest) -> RideResponse:
        # Verify user is a rider
        if not self.user_service.verify_user_role(user_id, "rider"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only riders can create ride requests"
            )
        
        # Calculate fare
        pickup_coords = request.pickup_coordinates.dict()
        drop_coords = request.drop_coordinates.dict()
        fare = self.fare_service.calculate_fare(pickup_coords, drop_coords)
        
        # Create ride data
        ride_data = {
            "ride_id": str(uuid.uuid4()),
            "user_id": user_id,
            "pickup": request.pickup,
            "drop": request.drop,
            "status": "pending",
            "payment_status": "pending",
            "requested_at": datetime.now().isoformat(),
            "fare": float(fare)
        }
        
        ride = self.ride_repo.create_ride(ride_data)
        return RideResponse(**ride)

class ApplyForRideUseCase:
    def __init__(self, ride_repo: RideRepository, app_repo: RideApplicationRepository, user_service: UserService):
        self.ride_repo = ride_repo
        self.app_repo = app_repo
        self.user_service = user_service
        self.location_service = LocationService()
    
    def execute(self, driver_id: str, request: RideApplicationRequest) -> Dict[str, str]:
        # Verify user is a driver
        if not self.user_service.verify_user_role(driver_id, "driver"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only drivers can apply for rides"
            )
        
        # Check if ride exists and is pending
        ride = self.ride_repo.get_ride_by_id(request.ride_id)
        if not ride or ride["status"] != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ride is not available for application"
            )
        
        # Check if driver already applied
        existing_app = self.app_repo.check_existing_application(request.ride_id, driver_id)
        if existing_app:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You have already applied for this ride"
            )
        
        # Create application
        location_json = self.location_service.format_location(
            request.current_location.latitude,
            request.current_location.longitude,
            request.current_location.address
        )
        
        app_data = {
            "application_id": str(uuid.uuid4()),
            "ride_id": request.ride_id,
            "driver_id": driver_id,
            "locations": location_json,
            "applied_at": datetime.now().isoformat()
        }
        
        self.app_repo.create_application(app_data)
        return {"message": "Successfully applied for ride"}

class GetPendingRidesUseCase:
    def __init__(self, ride_repo: RideRepository, user_service: UserService):
        self.ride_repo = ride_repo
        self.user_service = user_service
    
    def execute(self, driver_id: str) -> List[RideResponse]:
        # Verify user is a driver
        if not self.user_service.verify_user_role(driver_id, "driver"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only drivers can view pending rides"
            )
        
        rides = self.ride_repo.get_rides_by_status("pending")
        return [RideResponse(**ride) for ride in rides]

class SelectDriverUseCase:
    def __init__(self, ride_repo: RideRepository, app_repo: RideApplicationRepository):
        self.ride_repo = ride_repo
        self.app_repo = app_repo
    
    def execute(self, user_id: str, ride_id: str, driver_id: str) -> Dict[str, str]:
        # Verify user owns the ride
        ride = self.ride_repo.get_ride_by_id(ride_id)
        if not ride or ride["user_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to select driver for this ride"
            )
        
        if ride["status"] != "pending":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ride is not in pending status"
            )
        
        # Verify driver applied
        application = self.app_repo.check_existing_application(ride_id, driver_id)
        if not application:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Driver has not applied for this ride"
            )
        
        # Update ride
        self.ride_repo.update_ride(ride_id, {
            "driver_id": driver_id,
            "status": "confirmed"
        })
        
        return {"message": "Driver selected successfully"}