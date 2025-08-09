from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class RideCreate(BaseModel):
    rider_id: UUID
    driver_id: UUID
    origin: str
    destination: str

class RideUpdate(BaseModel):
    status: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    fare: float | None = None

class RideOut(BaseModel):
    id: UUID
    rider_id: UUID
    driver_id: UUID
    origin: str
    destination: str
    status: str
    requested_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    fare: float | None