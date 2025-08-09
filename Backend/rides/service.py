from uuid import UUID, uuid4
from datetime import datetime
from .models import Ride
from .schemas import RideCreate, RideUpdate

# In-memory storage for demonstration
rides_db: dict[UUID, Ride] = {}

def create_ride(data: RideCreate) -> Ride:
    ride_id = uuid4()
    ride = Ride(
        id=ride_id,
        rider_id=data.rider_id,
        driver_id=data.driver_id,
        origin=data.origin,
        destination=data.destination,
        status="requested",
        requested_at=datetime.utcnow(),
        started_at=None,
        completed_at=None,
        fare=None
    )
    rides_db[ride_id] = ride
    return ride

def get_ride(ride_id: UUID) -> Ride | None:
    return rides_db.get(ride_id)

def list_rides() -> list[Ride]:
    return list(rides_db.values())

def update_ride(ride_id: UUID, data: RideUpdate) -> Ride | None:
    ride = rides_db.get(ride_id)
    if not ride:
        return None
    update_data = data.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(ride, key, value)
    rides_db[ride_id] = ride
    return ride

def delete_ride(ride_id: UUID) -> bool:
    if ride_id in rides_db:
        del rides_db[ride_id]
        return True
    return False