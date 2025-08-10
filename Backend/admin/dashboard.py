from fastapi import APIRouter, Depends
from db.database import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/admin/dashboard", tags=["Admin Dashboard"])

@router.get("/", summary="Get admin dashboard overview")
def get_dashboard_overview(db: Session = Depends(get_db)):
    """
    Returns summary statistics for the admin dashboard.
    """
    # Example: Replace with actual queries
    total_users = db.execute("SELECT COUNT(*) FROM users").scalar()
    total_drivers = db.execute("SELECT COUNT(*) FROM driver_profiles").scalar()
    total_rides = db.execute("SELECT COUNT(*) FROM rides").scalar()
    total_payments = db.execute("SELECT COUNT(*) FROM payments").scalar()

    return {
        "total_users": total_users,
        "total_drivers": total_drivers,
        "total_rides": total_rides,
        "total_payments": total_payments
    }
