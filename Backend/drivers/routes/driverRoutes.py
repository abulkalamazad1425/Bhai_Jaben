from fastapi import APIRouter, HTTPException
from ..services.driverServices import DriverService
from ..schemas.driverSchemas import DriverProfileOut, DriverProfileUpdate , AvailabilityUpdate, RideActionResponse
driver_router = APIRouter(prefix="/driver", tags=["Driver"])
driver_service = DriverService()

@driver_router.get("/profile/{user_id}", response_model=DriverProfileOut)
def get_driver_profile(user_id: str):
    try:
        return driver_service.get_driver_profile(user_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

@driver_router.put("/profile/{user_id}", response_model=DriverProfileOut)
def update_profile(user_id: str, updates: DriverProfileUpdate):
    try:
        return driver_service.update_driver_profile(user_id, updates)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")

# ----- NEW: Toggle Availability -----
@driver_router.patch("/availability/{user_id}", response_model=RideActionResponse)
def toggle_availability(user_id: str, update: AvailabilityUpdate):
    try:
        return driver_service.toggle_availability(user_id, update.is_available)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


# ----- NEW: Accept Ride -----
@driver_router.post("/rides/{ride_id}/accept/{user_id}", response_model=RideActionResponse)
def accept_ride(user_id: str, ride_id: str):
    try:
        return driver_service.accept_ride(user_id, ride_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")


# ----- NEW: Reject Ride -----
@driver_router.post("/rides/{ride_id}/reject/{user_id}", response_model=RideActionResponse)
def reject_ride(user_id: str, ride_id: str):
    try:
        return driver_service.reject_ride(user_id, ride_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Unexpected error: {str(e)}")