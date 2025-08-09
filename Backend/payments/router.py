from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Dict, Optional
from .service import PaymentService
from .schemas import (
    PaymentResponse, OnlinePaymentInitResponse, CashPaymentRequest, 
    OnlinePaymentRequest, PaymentSuccessResponse, PaymentFailureResponse,
    PaymentCancelResponse
)
from auth.services.login_service import LoginService
from .database_config import DatabaseConfig

router = APIRouter(prefix='/payment', tags=['Payments'])

# Initialize services
database_client = DatabaseConfig().get_client()
payment_service = PaymentService(database_client)
login_service = LoginService(database_client)

@router.post("/cash/{ride_id}", response_model=PaymentResponse)
def process_cash_payment(
    ride_id: str,
    current_user_id: str = Depends(login_service.get_current_user)
) -> PaymentResponse:
    """Driver marks cash payment as completed"""
    return payment_service.process_cash_payment(current_user_id, ride_id)

@router.post("/online/{ride_id}", response_model=OnlinePaymentInitResponse)
def initiate_online_payment(
    ride_id: str,
    current_user_id: str = Depends(login_service.get_current_user)
) -> OnlinePaymentInitResponse:
    """Rider initiates online payment"""
    return payment_service.initiate_online_payment(current_user_id, ride_id)

@router.get("/status/{ride_id}")
def get_payment_status(
    ride_id: str,
    current_user_id: str = Depends(login_service.get_current_user)
) -> Dict[str, str]:
    """Get payment status for a ride"""
    return payment_service.get_ride_payment_status(ride_id, current_user_id)

@router.get("/ride/{ride_id}", response_model=Optional[PaymentResponse])
def get_payment_by_ride(
    ride_id: str,
    current_user_id: str = Depends(login_service.get_current_user)
) -> Optional[PaymentResponse]:
    """Get payment details for a specific ride"""
    return payment_service.get_payment_by_ride_id(ride_id, current_user_id)

@router.post("/success")
@router.get("/success")
async def payment_success(request: Request):
    """Handle successful payment callback from SSLCommerz"""
    try:
        print(f"=== Payment Success Endpoint Called - Method: {request.method} ===")
        
        payment_data = {}
        
        # Handle POST request (IPN - Server to Server)
        if request.method == "POST":
            form_data = await request.form()
            payment_data = dict(form_data)
            print("POST callback received:", payment_data)
        
        # Handle GET request (Browser redirect)
        else:
            payment_data = dict(request.query_params)
            print("GET callback received:", payment_data)
        
        # Process the payment
        print("Processing payment success...")
        result = payment_service.handle_payment_success(payment_data)
        print("Payment processed successfully:", result)
        
        # For POST requests (IPN), return simple JSON response
        if request.method == "POST":
            return {
                "status": "SUCCESS",
                "message": "Payment processed successfully",
                "ride_id": result.ride_id,
                "payment_id": result.payment_id
            }
        
        # For GET requests (browser), return HTML page
        else:
            return HTMLResponse(
                content=f"""
                <html>
                    <head>
                        <title>Payment Successful</title>
                        <style>
                            body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                            .success {{ color: green; }}
                            .container {{ max-width: 600px; margin: 0 auto; }}
                            .detail {{ margin: 10px 0; padding: 5px; background: #f0f0f0; }}
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h1 class="success">🎉 Payment Successful!</h1>
                            <p>Your ride payment has been processed successfully.</p>
                            
                            <div class="detail"><strong>Ride ID:</strong> {result.ride_id}</div>
                            <div class="detail"><strong>Payment ID:</strong> {result.payment_id}</div>
                            <div class="detail"><strong>Transaction ID:</strong> {result.transaction_id}</div>
                            <div class="detail"><strong>Amount:</strong> ৳{result.amount}</div>
                            <div class="detail"><strong>Status:</strong> {result.status}</div>
                            
                            <p>Thank you for using our ride service!</p>
                            <button onclick="window.close()" style="padding: 10px 20px; background: green; color: white; border: none; cursor: pointer;">Close Window</button>
                        </div>
                    </body>
                </html>
                """,
                status_code=200
            )
            
    except Exception as e:
        print(f"Payment success handling error: {str(e)}")
        import traceback
        print(traceback.format_exc())
        
        # For POST requests, return JSON error
        if request.method == "POST":
            return {
                "status": "ERROR",
                "message": str(e)
            }
        
        # For GET requests, return HTML error page
        else:
            return HTMLResponse(
                content=f"""
                <html>
                    <head>
                        <title>Payment Error</title>
                        <style>
                            body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                            .error {{ color: red; }}
                        </style>
                    </head>
                    <body>
                        <h1 class="error">❌ Payment Processing Error</h1>
                        <p>There was an error processing your payment.</p>
                        <p>Error: {str(e)}</p>
                        <button onclick="window.close()">Close</button>
                    </body>
                </html>
                """,
                status_code=400
            )

@router.post("/failed")
@router.get("/failed") 
async def payment_failed(request: Request):
    """Handle failed payment callback from SSLCommerz"""
    try:
        print(f"=== Payment Failed Endpoint Called - Method: {request.method} ===")
        
        payment_data = {}
        
        if request.method == "POST":
            form_data = await request.form()
            payment_data = dict(form_data)
            print("POST failure callback received:", payment_data)
        else:
            payment_data = dict(request.query_params)
            print("GET failure callback received:", payment_data)
        
        result = payment_service.handle_payment_failure(payment_data)
        print("Payment failure processed:", result)
        
        # For POST requests (IPN)
        if request.method == "POST":
            return {
                "status": "FAILED",
                "message": result.message,
                "ride_id": result.ride_id
            }
        
        # For GET requests (browser)
        else:
            return HTMLResponse(
                content=f"""
                <html>
                    <head>
                        <title>Payment Failed</title>
                        <style>
                            body {{ font-family: Arial, sans-serif; text-align: center; padding: 50px; }}
                            .error {{ color: red; }}
                            .container {{ max-width: 600px; margin: 0 auto; }}
                        </style>
                    </head>
                    <body>
                        <div class="container">
                            <h1 class="error">❌ Payment Failed</h1>
                            <p>Your payment could not be processed.</p>
                            <p><strong>Ride ID:</strong> {result.ride_id or 'N/A'}</p>
                            <p><strong>Error:</strong> {result.error}</p>
                            <p>Please try again or contact support.</p>
                            <button onclick="window.close()">Close</button>
                        </div>
                    </body>
                </html>
                """,
                status_code=400
            )
            
    except Exception as e:
        print(f"Payment failure handling error: {str(e)}")
        if request.method == "POST":
            return {"status": "ERROR", "message": str(e)}
        else:
            return HTMLResponse(
                content=f"<h1>Error</h1><p>{str(e)}</p>",
                status_code=400
            )

# IPN (Instant Payment Notification) endpoint for SSLCommerz
@router.post("/ipn")
def payment_ipn(request: Request):
    """Handle IPN callback from SSLCommerz for real-time payment status updates"""
    try:
        payment_data = dict(request.form()) if hasattr(request, 'form') else {}
        
        # Process the payment based on status
        status = payment_data.get('status')
        if status == 'VALID':
            payment_service.handle_payment_success(payment_data)
        else:
            payment_service.handle_payment_failure(payment_data)
        
        return {"status": "OK"}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}

