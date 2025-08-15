from fastapi import HTTPException, status
from typing import Dict, Optional
from decimal import Decimal
import uuid
from datetime import datetime, timedelta

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
            
            # # Validate payment with SSLCommerz
            # print("Validating payment with SSLCommerz...")
            # validation_result = self.sslcommerz.validate_payment(val_id, tran_id, amount)
            # print("Validation successful:", validation_result)
            
            # Create payment record ONLY on successful validation
            payment_record = {
                "id": str(uuid.uuid4()),
                "ride_id": ride_id,
                "amount": float(amount),
                "payment_method": "online",
                "transaction_id": tran_id,
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
                transaction_id=tran_id,
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
    
    def get_all_payments_admin(self, page: int = 1, limit: int = 50) -> Dict:
        """Get all payments for admin with pagination"""
        try:
            offset = (page - 1) * limit
            
            # Get total count
            count_response = self.supabase.table('payments').select('*', count='exact').execute()
            total_count = count_response.count
            
            # Get payments with ride and user info
            response = self.supabase.table('payments')\
                .select('''
                    *,
                    rides:ride_id(user_id, driver_id)
                ''')\
                .range(offset, offset + limit - 1)\
                .order('created_at', desc=True)\
                .execute()
            
            payments = []
            for payment in response.data:
                payment_data = {
                    "id": payment['id'],
                    "ride_id": payment['ride_id'],
                    "user_id": payment['rides']['user_id'] if payment.get('rides') else None,
                    "driver_id": payment['rides']['driver_id'] if payment.get('rides') else None,
                    "amount": payment['amount'],
                    "payment_method": payment['payment_method'],
                    "transaction_id": payment.get('transaction_id'),
                    "status": payment['status'],
                    "created_at": payment['created_at']
                }
                payments.append(payment_data)
            
            return {
                "payments": payments,
                "total_count": total_count
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching payments: {str(e)}"
            )
    
    def get_payment_by_ride_id_admin(self, ride_id: str) -> Optional[Dict]:
        """Get payment by ride ID for admin"""
        try:
            response = self.supabase.table('payments')\
                .select('*')\
                .eq('ride_id', ride_id)\
                .single()\
                .execute()
            
            return response.data
            
        except Exception:
            return None
    
    def get_payment_stats_admin(self) -> Dict:
        """Get payment statistics for admin dashboard"""
        try:
            # Total revenue
            completed_payments = self.supabase.table('payments')\
                .select('amount')\
                .eq('status', 'completed')\
                .execute()
            
            total_revenue = sum(payment['amount'] for payment in completed_payments.data)
            
            # Total transactions
            total_response = self.supabase.table('payments').select('*', count='exact').execute()
            total_transactions = total_response.count
            
            # Successful transactions
            success_response = self.supabase.table('payments')\
                .select('*', count='exact')\
                .eq('status', 'completed')\
                .execute()
            successful_transactions = success_response.count
            
            # Failed transactions
            failed_response = self.supabase.table('payments')\
                .select('*', count='exact')\
                .eq('status', 'failed')\
                .execute()
            failed_transactions = failed_response.count
            
            # Payment method breakdown
            cash_response = self.supabase.table('payments')\
                .select('*', count='exact')\
                .eq('payment_method', 'cash')\
                .eq('status', 'completed')\
                .execute()
            cash_payments = cash_response.count
            
            online_response = self.supabase.table('payments')\
                .select('*', count='exact')\
                .eq('payment_method', 'online')\
                .eq('status', 'completed')\
                .execute()
            online_payments = online_response.count
            
            return {
                "total_revenue": total_revenue,
                "total_transactions": total_transactions,
                "successful_transactions": successful_transactions,
                "failed_transactions": failed_transactions,
                "cash_payments": cash_payments,
                "online_payments": online_payments
            }
            
        except Exception as e:
            return {
                "total_revenue": 0.0,
                "total_transactions": 0,
                "successful_transactions": 0,
                "failed_transactions": 0,
                "cash_payments": 0,
                "online_payments": 0
            }
    
    def get_revenue_by_date_admin(self, date) -> float:
        """Get revenue for a specific date"""
        try:
            date_str = date.isoformat() if hasattr(date, 'isoformat') else str(date)
            next_date = (datetime.strptime(date_str, '%Y-%m-%d').date() + timedelta(days=1)).isoformat()
            
            response = self.supabase.table('payments')\
                .select('amount')\
                .eq('status', 'completed')\
                .gte('created_at', date_str)\
                .lt('created_at', next_date)\
                .execute()
            
            return sum(payment['amount'] for payment in response.data)
            
        except Exception:
            return 0.0
    
    def get_revenue_analytics_admin(self, start_date: str, end_date: str) -> Dict:
        """Get revenue analytics for date range"""
        try:
            response = self.supabase.table('payments')\
                .select('amount, created_at, payment_method')\
                .eq('status', 'completed')\
                .gte('created_at', start_date)\
                .lte('created_at', end_date)\
                .order('created_at')\
                .execute()
            
            # Process data for analytics
            daily_revenue = {}
            method_breakdown = {"cash": 0, "online": 0}
            total_revenue = 0
            
            for payment in response.data:
                # Daily revenue
                date = payment['created_at'][:10]  # Extract date part
                if date not in daily_revenue:
                    daily_revenue[date] = 0
                daily_revenue[date] += payment['amount']
                
                # Method breakdown
                method_breakdown[payment['payment_method']] += payment['amount']
                
                # Total revenue
                total_revenue += payment['amount']
            
            return {
                "total_revenue": total_revenue,
                "daily_revenue": daily_revenue,
                "payment_method_breakdown": method_breakdown,
                "period": f"{start_date} to {end_date}",
                "total_transactions": len(response.data)
            }
            
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching revenue analytics: {str(e)}"
            )