from fastapi import APIRouter, HTTPException
from uuid import UUID
from .models import Ride

router = APIRouter(
    prefix="/rides",
    tags=["rides"]
)

# In-memory storage for demonstration
rides_db: dict[UUID, Ride] = {}

@router.post("/", response_model=Ride)
def create_ride(ride: Ride):
    if ride.id in rides_db:
        raise HTTPException(status_code=400, detail="Ride already exists")
    rides_db[ride.id] = ride
    return ride

@router.get("/{ride_id}", response_model=Ride)
def get_ride(ride_id: UUID):
    ride = rides_db.get(ride_id)
    if not ride:
        raise HTTPException(status_code=404, detail="Ride not found")
    return ride

@router.get("/", response_model=list[Ride])
def list_rides():
    return list(rides_db.values())