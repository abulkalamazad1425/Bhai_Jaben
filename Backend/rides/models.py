from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class Ride(BaseModel):
    id: UUID
    rider_id: UUID  # references users.id
    driver_id: UUID  # references driver_profiles.user_id
    origin: str
    destination: str
    status: str  # e.g., 'requested', 'ongoing', 'completed', 'cancelled'
    requested_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    fare: float | None = None