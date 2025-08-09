from fastapi import HTTPException, status
from typing import Dict, Optional
from decimal import Decimal
import uuid
from datetime import datetime

from .repositories.payment_repository import PaymentRepository
from .services.sslcommerz_service import SSLCommerzService
from .schemas import (
    PaymentResponse, OnlinePaymentInitResponse, CashPaymentRequest, 
    OnlinePaymentRequest, PaymentSuccessResponse, PaymentFailureResponse, 
    PaymentCancelResponse
)
from rides.service import RideService
from users.service import UserService

class PaymentService:
    def __init__(self, supabase_client):
        self.payment_repo = PaymentRepository(supabase_client)
        self.ride_service = RideService(supabase_client)
        self.user_service = UserService(supabase_client)
        self.sslcommerz = SSLCommerzService()
    
    def process_cash_payment(self, driver_id: str, ride_id: str) -> PaymentResponse:
        """Process cash payment - only driver can mark as paid"""
        try:
            # Validate ride for payment using rides service
            ride_validation = self.ride_service.validate_ride_for_payment(ride_id)
            
            # Verify driver is assigned to this ride using rides service
            if not self.ride_service.verify_driver_for_ride(driver_id, ride_id):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Only the assigned driver can mark cash payment"
                )
            
            # Check if payment record already exists
            existing_payment = self.payment_repo.get_payment_by_ride_id(ride_id)
            if existing_payment and existing_payment["status"] == "completed":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Payment already exists for this ride"
                )
            
            # Create or update payment record
            payment_id = str(uuid.uuid4())
            payment_data = {
                "id": payment_id,
                "ride_id": ride_id,
                "amount": float(ride_validation["fare"]),
                "payment_method": "cash",
                "transaction_id": None,
                "status": "completed",
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            if existing_payment:
                # Update existing payment
                payment = self.payment_repo.update_payment(existing_payment["id"], {
                    "status": "completed",
                    "payment_method": "cash",
                    "transaction_id": None,
                    "updated_at": datetime.now().isoformat()
                })
            else:
                # Create new payment
                payment = self.payment_repo.create_payment(payment_data)
            
            # Update ride payment status using rides service
            self.ride_service.update_ride_payment_status(ride_id, "paid")
            
            return PaymentResponse(**payment)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    def initiate_online_payment(self, user_id: str, ride_id: str) -> OnlinePaymentInitResponse:
    """Initiate online payment for rider - DON'T create payment record yet"""
    try:
        # Validate ride for payment using rides service
        ride_validation = self.ride_service.validate_ride_for_payment(ride_id)
        
        # Verify user is the rider using rides service
        if not self.ride_service.verify_rider_for_ride(user_id, ride_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the rider can make payment"
            )
        
        # Check if payment record already exists and is completed
        existing_payment = self.payment_repo.get_payment_by_ride_id(ride_id)
        if existing_payment and existing_payment["status"] == "completed":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment already completed for this ride"
            )
        
        # Get user info for payment
        user_info = self.user_service.get_user_data(user_id)
        
        # Prepare customer info for SSLCommerz
        customer_info = {
            "name": user_info["name"],
            "email": user_info["email"],
            "phone": user_info["phone"],
            "address": "Dhaka, Bangladesh",
            "city": "Dhaka"
        }
        
        # Set callback URLs - IMPORTANT: Use your actual server URL
        custom_urls = {
            "success_url": f"http://127.0.0.1:8002/payment/success",
            "fail_url": f"http://127.0.0.1:8002/payment/failed",
            "cancel_url": f"http://127.0.0.1:8002/payment/cancel"
        }
        
        # Initiate payment with SSLCommerz (NO database entry created)
        sslcommerz_response = self.sslcommerz.initiate_payment(
            amount=float(ride_validation["fare"]),
            customer_info=customer_info,
            ride_id=ride_id,
            custom_urls=custom_urls
        )
        
        return OnlinePaymentInitResponse(
            payment_url=sslcommerz_response.GatewayPageURL,
            session_key=sslcommerz_response.sessionkey
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

def handle_payment_success(self, payment_data: Dict) -> PaymentSuccessResponse:
    """Handle successful payment callback - CREATE payment entry here ONLY"""
    try:
        print("=== Payment Success Callback Data ===")
        print(payment_data)
        
        val_id = payment_data.get('val_id')
        tran_id = payment_data.get('tran_id')
        amount = payment_data.get('amount')
        ride_id = payment_data.get('value_a')  # We stored ride_id in value_a
        
        print(f"Extracted data: val_id={val_id}, tran_id={tran_id}, amount={amount}, ride_id={ride_id}")
        
        if not all([val_id, tran_id, amount, ride_id]):
            print("Missing required payment data")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Missing required payment data"
            )
        
        # Check if payment record already exists for this ride
        existing_payment = self.payment_repo.get_payment_by_ride_id(ride_id)
        if existing_payment and existing_payment["status"] == "completed":
            print("Payment already processed for this ride")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Payment already processed for this ride"
            )
        
        # Validate payment with SSLCommerz
        print("Validating payment with SSLCommerz...")
        validation_result = self.sslcommerz.validate_payment(val_id, tran_id, amount)
        print("Validation successful:", validation_result)
        
        # Create payment record ONLY on successful validation
        payment_record = {
            "id": str(uuid.uuid4()),
            "ride_id": ride_id,
            "amount": float(amount),
            "payment_method": "online",
            "transaction_id": validation_result.get('tran_id'),
            "status": "completed",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        print("Creating payment record:", payment_record)
        payment = self.payment_repo.create_payment(payment_record)
        print("Payment record created:", payment)
        
        # Update ride payment status using rides service
        print("Updating ride payment status...")
        self.ride_service.update_ride_payment_status(ride_id, "paid")
        print("Ride payment status updated to 'paid'")
        
        return PaymentSuccessResponse(
            message="Payment completed successfully",
            ride_id=ride_id,
            payment_id=payment["id"],
            transaction_id=validation_result.get('tran_id'),
            amount=amount,
            payment_method="online",
            status="completed"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Payment processing error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Payment processing error: {str(e)}"
        )

def handle_payment_failure(self, payment_data: Dict) -> PaymentFailureResponse:
    """Handle failed payment callback - DON'T create payment record"""
    try:
        print("=== Payment Failure Callback Data ===")
        print(payment_data)
        
        ride_id = payment_data.get('value_a')
        error_reason = payment_data.get('error', payment_data.get('failedreason', 'Payment failed'))
        
        # DON'T create payment record for failures
        # Just update ride status if needed
        if ride_id:
            print(f"Updating ride {ride_id} payment status to failed")
            self.ride_service.update_ride_payment_status(ride_id, "failed")
        
        return PaymentFailureResponse(
            message="Payment failed",
            ride_id=ride_id,
            error=error_reason
        )
        
    except Exception as e:
        print(f"Payment failure handling error: {str(e)}")
        return PaymentFailureResponse(
            message="Payment failed",
            ride_id=ride_id,
            error=str(e)
        )

def handle_payment_cancel(self, payment_data: Dict) -> PaymentCancelResponse:
    """Handle cancelled payment callback - DON'T create payment record"""
    try:
        print("=== Payment Cancel Callback Data ===")
        print(payment_data)
        
        ride_id = payment_data.get('value_a')
        
        # DON'T create payment record for cancellations
        # Keep ride payment status as pending (user can try again)
        
        return PaymentCancelResponse(
            message="Payment cancelled by user",
            ride_id=ride_id
        )
        
    except Exception as e:
        print(f"Payment cancellation error: {str(e)}")
        return PaymentCancelResponse(
            message="Payment cancellation error",
            ride_id=ride_id
        )
    
    def get_payment_by_ride_id(self, ride_id: str, current_user_id: str) -> Optional[PaymentResponse]:
        """Get payment details for a ride with authorization"""
        try:
            # Get ride details using rides service
            ride_details = self.ride_service.get_ride_payment_details(ride_id)
            
            # Check if user has permission to view payment
            if current_user_id not in [ride_details["user_id"], ride_details.get("driver_id")]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to view this payment"
                )
            
            # Get payment record
            payment = self.payment_repo.get_payment_by_ride_id(ride_id)
            if payment:
                return PaymentResponse(**payment)
            return None
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )
    
    def get_ride_payment_status(self, ride_id: str, current_user_id: str) -> Dict[str, str]:
        """Get payment status for a ride"""
        try:
            # Get ride details using rides service
            ride_details = self.ride_service.get_ride_payment_details(ride_id)
            
            # Check if user has permission to view
            if current_user_id not in [ride_details["user_id"], ride_details.get("driver_id")]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You don't have permission to view this ride"
                )
            
            # Get payment details
            payment = self.payment_repo.get_payment_by_ride_id(ride_id)
            payment_status_detail = "No payment record"
            if payment:
                payment_status_detail = payment["status"]
            
            return {
                "ride_id": ride_id,
                "payment_status": ride_details["payment_status"],
                "payment_record_status": payment_status_detail,
                "fare": str(ride_details.get("fare", 0)),
                "ride_status": ride_details["status"]
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e)
            )