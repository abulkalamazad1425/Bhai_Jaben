from fastapi import APIRouter, HTTPException
from ..services.driverServices import DriverService
from ..schemas.driverSchemas import DriverProfileOut, DriverProfileUpdate 
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