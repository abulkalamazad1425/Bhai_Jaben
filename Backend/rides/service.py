from fastapi import HTTPException, status
from typing import List, Dict, Optional
import uuid
from .repositories.ride_repository import RideRepository, RideApplicationRepository
from .repositories.rating_repository import RatingRepository
from .use_cases.ride_use_cases import CreateRideUseCase, ApplyForRideUseCase, GetPendingRidesUseCase, SelectDriverUseCase
from .schemas import (
    RideCreateRequest, RideResponse, RideApplicationRequest, RideApplicationResponse,
    RideRatingRequest, RideRatingResponse, RideWithRatingsResponse, 
    UserRatingsSummary, DriverRatingsSummary
)
from .websocket.connection_manager import connection_manager
from .domain.services import LocationService
from users.service import UserService
from drivers.service import DriverService
from datetime import datetime

class RideService:
    def __init__(self, supabase_client):
        self.ride_repo = RideRepository(supabase_client)
        self.app_repo = RideApplicationRepository(supabase_client)
        self.rating_repo = RatingRepository(supabase_client)  # Add rating repository
        self.user_service = UserService(supabase_client)
        self.driver_service = DriverService(supabase_client)
        self.location_service = LocationService()
        
        # Initialize use cases
        self.create_ride_use_case = CreateRideUseCase(self.ride_repo, self.user_service)
        self.apply_ride_use_case = ApplyForRideUseCase(self.ride_repo, self.app_repo, self.user_service)
        self.get_pending_rides_use_case = GetPendingRidesUseCase(self.ride_repo, self.user_service)
        self.select_driver_use_case = SelectDriverUseCase(self.ride_repo, self.app_repo)
       
        
        
    
    async def create_ride(self, user_id: str, request: RideCreateRequest) -> RideResponse:
        ride = self.create_ride_use_case.execute(user_id, request)
        
        # Notify all drivers about new ride
        await connection_manager.broadcast_to_drivers({
            "type": "new_ride",
            "message": "New ride request available",
            "data": ride.dict()
        }, await self._get_available_driver_ids())
        
        return ride
    
    async def apply_for_ride(self, driver_id: str, request: RideApplicationRequest) -> Dict[str, str]:
        result = self.apply_ride_use_case.execute(driver_id, request)
        
        # Get ride details
        ride = self.ride_repo.get_ride_by_id(request.ride_id)
        if ride:
            # Notify rider about new application
            await connection_manager.send_personal_message({
                "type": "new_application",
                "message": "A driver has applied for your ride",
                "data": {"ride_id": request.ride_id}
            }, ride["user_id"])
        
        return result
    
    def get_pending_rides(self, driver_id: str) -> List[RideResponse]:
        return self.get_pending_rides_use_case.execute(driver_id)
    
    def get_ride_applications(self, user_id: str, ride_id: str) -> List[RideApplicationResponse]:
        try:
            # Verify user owns the ride
            ride = self.ride_repo.get_ride_by_id(ride_id)
            if not ride or ride["user_id"] != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to view applications for this ride"
                )
            
            # Get applications (without driver details)
            applications = self.app_repo.get_applications_by_ride_id_simple(ride_id)
            
            result = []
            for app in applications:
                try:
                    # Get driver profile from driver service
                    driver_profile = self.driver_service.get_driver_profile_for_ride(app["driver_id"])
                    
                    # Parse location data
                    location_data = self.location_service.parse_location(app.get("locations", "{}"))
                    
                    result.append(RideApplicationResponse(
                        application_id=app["application_id"],
                        ride_id=app["ride_id"],
                        driver_id=app["driver_id"],
                        applied_at=app["applied_at"],
                        driver_name=driver_profile["name"],
                        driver_phone=driver_profile["phone"],
                        license=driver_profile["license"],
                        vehicle_info=driver_profile["vehicle_info"],
                        current_location={
                            "latitude": location_data.get("latitude", 0.0),
                            "longitude": location_data.get("longitude", 0.0),
                            "address": location_data.get("address")
                        }
                    ))
                except Exception as e:
                    # Skip applications where driver profile cannot be retrieved
                    print(f"Error getting driver profile for {app['driver_id']}: {str(e)}")
                    continue
            
            return result
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    async def select_driver(self, user_id: str, ride_id: str, driver_id: str) -> Dict[str, str]:
        result = self.select_driver_use_case.execute(user_id, ride_id, driver_id)
        
        # Notify selected driver
        await connection_manager.send_personal_message({
            "type": "ride_confirmed",
            "message": "You have been selected for a ride",
            "data": {"ride_id": ride_id}
        }, driver_id)
        
        # Notify other applicants that ride is no longer available
        applications = self.app_repo.get_applications_by_ride_id_simple(ride_id)
        for app in applications:
            if app["driver_id"] != driver_id:
                await connection_manager.send_personal_message({
                    "type": "ride_unavailable",
                    "message": "Ride is no longer available",
                    "data": {"ride_id": ride_id}
                }, app["driver_id"])
        
        return result
    
    async def start_ride(self, driver_id: str, ride_id: str) -> Dict[str, str]:
        ride = self.ride_repo.get_ride_by_id(ride_id)
        if not ride or ride["driver_id"] != driver_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to start this ride"
            )
        
        if ride["status"] != "confirmed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ride must be confirmed to start"
            )
        
        self.ride_repo.update_ride(ride_id, {
            "status": "ongoing",
            "start_time": datetime.now().isoformat()
        })
        
        # Notify rider
        await connection_manager.send_personal_message({
            "type": "ride_started",
            "message": "Your ride has started",
            "data": {"ride_id": ride_id}
        }, ride["user_id"])
        
        return {"message": "Ride started successfully"}
    
    async def complete_ride(self, driver_id: str, ride_id: str) -> Dict[str, str]:
        ride = self.ride_repo.get_ride_by_id(ride_id)
        if not ride or ride["driver_id"] != driver_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to complete this ride"
            )
        
        if ride["status"] != "ongoing":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ride must be ongoing to complete"
            )
        
        self.ride_repo.update_ride(ride_id, {
            "status": "completed",
            "end_time": datetime.now().isoformat(),
            "completed_at": datetime.now().isoformat()  # Add completion timestamp
        })
        
        # Notify rider
        await connection_manager.send_personal_message({
            "type": "ride_completed",
            "message": "Your ride has been completed. You can now rate your driver!",
            "data": {"ride_id": ride_id, "can_rate": True}
        }, ride["user_id"])
        
        # Notify driver they can rate the rider
        await connection_manager.send_personal_message({
            "type": "ride_completed",
            "message": "Ride completed successfully. You can now rate the rider!",
            "data": {"ride_id": ride_id, "can_rate": True}
        }, driver_id)
        
        return {"message": "Ride completed successfully"}
    
    async def cancel_ride(self, user_id: str, ride_id: str, cancel_reason: str) -> Dict[str, str]:
        ride = self.ride_repo.get_ride_by_id(ride_id)
        if not ride:
            raise HTTPException(status_code=404, detail="Ride not found")
        
        # Check permissions
        if user_id not in [ride["user_id"], ride.get("driver_id")]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to cancel this ride"
            )
        
        if ride["status"] not in ["pending", "confirmed", "ongoing"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ride cannot be cancelled in current status"
            )
        
        self.ride_repo.update_ride(ride_id, {
            "status": "cancelled",
            "cancel_reason": cancel_reason
        })
        
        # Notify other party
        other_user = ride["driver_id"] if user_id == ride["user_id"] else ride["user_id"]
        if other_user:
            await connection_manager.send_personal_message({
                "type": "ride_cancelled",
                "message": "The ride has been cancelled",
                "data": {"ride_id": ride_id, "reason": cancel_reason}
            }, other_user)
        
        return {"message": "Ride cancelled successfully"}
    
    async def _get_available_driver_ids(self) -> List[str]:
        # Get all active drivers from connected users
        driver_ids = []
        for user_id in connection_manager.active_connections.keys():
            try:
                if self.user_service.verify_user_role(user_id, "driver"):
                    driver_ids.append(user_id)
            except:
                continue
        return driver_ids
    
    # New methods for payment service
    def get_ride_for_payment(self, ride_id: str) -> Optional[Dict]:
        """Get ride details for payment processing"""
        try:
            ride = self.ride_repo.get_ride_by_id(ride_id)
            return ride
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching ride: {str(e)}"
            )

    def verify_driver_for_ride(self, driver_id: str, ride_id: str) -> bool:
        """Verify if driver is assigned to the ride"""
        try:
            ride = self.ride_repo.get_ride_by_id(ride_id)
            if not ride:
                return False
            return ride.get("driver_id") == driver_id
        except Exception:
            return False

    def verify_rider_for_ride(self, user_id: str, ride_id: str) -> bool:
        """Verify if user is the rider for the ride"""
        try:
            ride = self.ride_repo.get_ride_by_id(ride_id)
            if not ride:
                return False
            return ride.get("user_id") == user_id
        except Exception:
            return False

    def update_ride_payment_status(self, ride_id: str, payment_status: str) -> Dict[str, str]:
        """Update payment status of a ride"""
        try:
            # Validate payment status
            valid_statuses = ['pending', 'paid', 'failed', 'refunded']
            if payment_status not in valid_statuses:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid payment status. Must be one of: {valid_statuses}"
                )

            # Check if ride exists
            ride = self.ride_repo.get_ride_by_id(ride_id)
            if not ride:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Ride not found"
                )

            # Update payment status
            updated_ride = self.ride_repo.update_ride(ride_id, {
                "payment_status": payment_status,
                "updated_at": datetime.now().isoformat()
            })

            if not updated_ride:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to update ride payment status"
                )

            return {"message": f"Ride payment status updated to {payment_status}"}

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error updating payment status: {str(e)}"
            )

    def get_ride_payment_details(self, ride_id: str) -> Dict:
        """Get ride payment-related details"""
        try:
            ride = self.ride_repo.get_ride_by_id(ride_id)
            if not ride:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Ride not found"
                )

            return {
                "ride_id": ride["ride_id"],
                "user_id": ride["user_id"],
                "driver_id": ride.get("driver_id"),
                "status": ride["status"],
                "payment_status": ride["payment_status"],
                "fare": ride.get("fare"),
                "pickup": ride["pickup"],
                "drop": ride["drop"]
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching ride payment details: {str(e)}"
            )

    def validate_ride_for_payment(self, ride_id: str) -> Dict:
        """Validate if ride is ready for payment"""
        try:
            ride = self.ride_repo.get_ride_by_id(ride_id)
            if not ride:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Ride not found"
                )

            # Check if ride is completed
            if ride["status"] != "completed":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Ride must be completed before payment"
                )

            # Check if already paid
            if ride["payment_status"] == "paid":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Payment already completed"
                )

            # Check if fare is set
            if not ride.get("fare") or ride["fare"] <= 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid ride fare"
                )

            return {
                "valid": True,
                "ride_id": ride_id,
                "fare": ride["fare"],
                "user_id": ride["user_id"],
                "driver_id": ride.get("driver_id")
            }

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error validating ride for payment: {str(e)}"
            )
    
    # Rating methods
    async def rate_ride(self, rater_id: str, request: RideRatingRequest) -> RideRatingResponse:
        """Allow user or driver to rate after ride completion"""
        try:
            ride = self.ride_repo.get_ride_by_id(request.ride_id)
            if not ride:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Ride not found"
                )
            
            # Check if ride is completed
            if ride["status"] != "completed":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Can only rate completed rides"
                )
            
            # Determine rater type and who they're rating
            rater_type = None
            rated_user_id = None
            
            if rater_id == ride["user_id"]:
                # User is rating the driver
                rater_type = "user"
                rated_user_id = ride["driver_id"]
                if not rated_user_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="No driver assigned to this ride"
                    )
            elif rater_id == ride["driver_id"]:
                # Driver is rating the user
                rater_type = "driver"
                rated_user_id = ride["user_id"]
            else:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can only rate rides you participated in"
                )
            
            # Check if already rated
            existing_rating = self.rating_repo.get_rating_by_ride_and_rater(
                request.ride_id, rater_id
            )
            if existing_rating:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You have already rated this ride"
                )
            
            # Create rating
            rating_data = {
                "rating_id": str(uuid.uuid4()),
                "ride_id": request.ride_id,
                "rater_id": rater_id,
                "rater_type": rater_type,
                "rated_user_id": rated_user_id,
                "rating": request.rating,
                "comment": request.comment,
                "created_at": datetime.now().isoformat()
            }
            
            rating = self.rating_repo.create_rating(rating_data)
            
            # Notify the rated user
            await connection_manager.send_personal_message({
                "type": "new_rating",
                "message": f"You received a {request.rating}-star rating!",
                "data": {
                    "ride_id": request.ride_id,
                    "rating": request.rating,
                    "rater_type": rater_type
                }
            }, rated_user_id)
            
            return RideRatingResponse(**rating)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating rating: {str(e)}"
            )

    def get_ride_with_ratings(self, current_user_id: str, ride_id: str) -> RideWithRatingsResponse:
        """Get ride details with rating information"""
        try:
            ride = self.ride_repo.get_ride_by_id(ride_id)
            if not ride:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Ride not found"
                )
            
            # Check if user has permission to view this ride
            if current_user_id not in [ride["user_id"], ride.get("driver_id")]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to view this ride"
                )
            
            # Get ratings for this ride
            ratings = self.rating_repo.get_ratings_by_ride_id(ride_id)
            
            user_rating = None
            driver_rating = None
            
            for rating in ratings:
                if rating["rater_type"] == "user":
                    user_rating = RideRatingResponse(**rating)
                elif rating["rater_type"] == "driver":
                    driver_rating = RideRatingResponse(**rating)
            
            # Determine if current user can rate
            can_rate_driver = False
            can_rate_user = False
            
            if ride["status"] == "completed":
                if current_user_id == ride["user_id"] and not user_rating:
                    can_rate_driver = True
                elif current_user_id == ride["driver_id"] and not driver_rating:
                    can_rate_user = True
            
            return RideWithRatingsResponse(
                ride_id=ride["ride_id"],
                user_id=ride["user_id"],
                driver_id=ride.get("driver_id"),
                pickup=ride["pickup"],
                drop=ride["drop"],
                fare=ride.get("fare"),
                status=ride["status"],
                payment_status=ride["payment_status"],
                created_at=ride["created_at"],
                completed_at=ride.get("completed_at"),
                user_rating=user_rating,
                driver_rating=driver_rating,
                can_rate_driver=can_rate_driver,
                can_rate_user=can_rate_user
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching ride with ratings: {str(e)}"
            )

    def get_user_ratings_summary(self, user_id: str) -> UserRatingsSummary:
        """Get summary of ratings received by a user"""
        try:
            ratings = self.rating_repo.get_ratings_for_user(user_id)
            
            if not ratings:
                return UserRatingsSummary(
                    user_id=user_id,
                    total_ratings=0,
                    average_rating=0.0,
                    ratings_breakdown={1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
                )
            
            total_ratings = len(ratings)
            total_score = sum(rating["rating"] for rating in ratings)
            average_rating = round(total_score / total_ratings, 2)
            
            # Count ratings by star value
            breakdown = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            for rating in ratings:
                breakdown[rating["rating"]] += 1
            
            return UserRatingsSummary(
                user_id=user_id,
                total_ratings=total_ratings,
                average_rating=average_rating,
                ratings_breakdown=breakdown
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching user ratings: {str(e)}"
            )

    def get_driver_ratings_summary(self, driver_id: str) -> DriverRatingsSummary:
        """Get summary of ratings received by a driver"""
        try:
            ratings = self.rating_repo.get_ratings_for_driver(driver_id)
            
            if not ratings:
                return DriverRatingsSummary(
                    driver_id=driver_id,
                    total_ratings=0,
                    average_rating=0.0,
                    ratings_breakdown={1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
                )
            
            total_ratings = len(ratings)
            total_score = sum(rating["rating"] for rating in ratings)
            average_rating = round(total_score / total_ratings, 2)
            
            # Count ratings by star value
            breakdown = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
            for rating in ratings:
                breakdown[rating["rating"]] += 1
            
            return DriverRatingsSummary(
                driver_id=driver_id,
                total_ratings=total_ratings,
                average_rating=average_rating,
                ratings_breakdown=breakdown
            )
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching driver ratings: {str(e)}"
            )

    def get_my_completed_rides(self, current_user_id: str) -> List[RideWithRatingsResponse]:
        """Get all completed rides for current user with rating info"""
        try:
            # Check if user is a driver or regular user
            try:
                is_driver = self.user_service.verify_user_role(current_user_id, "driver")
            except:
                is_driver = False
            
            if is_driver:
                # Get rides where user is the driver
                rides = self.ride_repo.get_rides_by_driver_id(current_user_id, status="completed")
            else:
                # Get rides where user is the rider
                rides = self.ride_repo.get_rides_by_user_id(current_user_id, status="completed")
            
            result = []
            for ride in rides:
                try:
                    ride_with_ratings = self.get_ride_with_ratings(current_user_id, ride["ride_id"])
                    result.append(ride_with_ratings)
                except Exception as e:
                    # Skip rides that can't be processed
                    print(f"Error processing ride {ride['ride_id']}: {str(e)}")
                    continue
            
            return result
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching completed rides: {str(e)}"
            )

