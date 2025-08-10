from fastapi import APIRouter, Depends
from db.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/admin/drivers", tags=["Admin Drivers"])

@router.get("/", summary="Get all drivers")
def get_all_drivers(db: Session = Depends(get_db)):
    """
    Returns a list of all driver profiles.
    """
    drivers = db.execute("SELECT * FROM driver_profiles").fetchall()
    return [dict(row) for row in drivers]

@router.get("/{driver_id}", summary="Get driver by ID")
def get_driver_by_id(driver_id: int, db: Session = Depends(get_db)):
    """
    Returns details of a specific driver.
    """
    driver = db.execute(
        "SELECT * FROM driver_profiles WHERE id = :id", {"id": driver_id}
    ).fetchone()
    if driver:
        return dict(driver)
    return {"error": "Driver not found"}
