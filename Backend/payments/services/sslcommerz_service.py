import requests
import hashlib
import uuid
from typing import Dict, Optional
from ..config import PaymentConfig
from ..schemas import SSLCommerzRequest, SSLCommerzResponse, PaymentCallbackRequest
from fastapi import HTTPException, status

class SSLCommerzService:
    def __init__(self):
        self.config = PaymentConfig()
    
    def initiate_payment(self, 
                        amount: float, 
                        customer_info: Dict, 
                        ride_id: str,
                        custom_urls: Optional[Dict] = None) -> SSLCommerzResponse:
        """Initiate payment with SSLCommerz"""
        try:
            # Generate unique transaction ID
            tran_id = f"RIDE_{ride_id}_{uuid.uuid4().hex[:8]}"
            
            # Get callback URLs
            callback_urls = custom_urls or self.config.get_callback_urls()
            
            # Prepare payment request
            payment_data = {
                'store_id': self.config.SSLCOMMERZ_STORE_ID,
                'store_passwd': self.config.SSLCOMMERZ_STORE_PASSWORD,
                'total_amount': str(amount),
                'currency': 'BDT',
                'tran_id': tran_id,
                'success_url': callback_urls['success_url'],
                'fail_url': callback_urls['fail_url'],
                'cancel_url': callback_urls['cancel_url'],
                'ipn_url': callback_urls.get('ipn_url', callback_urls['success_url']),
                
                # Customer information
                'cus_name': customer_info.get('name', 'Customer'),
                'cus_email': customer_info.get('email', 'customer@example.com'),
                'cus_phone': customer_info.get('phone', '01700000000'),
                'cus_add1': customer_info.get('address', 'Dhaka'),
                'cus_city': customer_info.get('city', 'Dhaka'),
                'cus_country': 'Bangladesh',
                
                # Shipping information
                'shipping_method': 'NO',
                'ship_name': customer_info.get('name', 'Customer'),
                'ship_add1': customer_info.get('address', 'Dhaka'),
                'ship_city': customer_info.get('city', 'Dhaka'),
                'ship_country': 'Bangladesh',
                
                # Product information
                'product_name': f'Ride Payment - {ride_id}',
                'product_category': 'Transportation',
                'product_profile': 'general',
                
                # Optional parameters
                'value_a': ride_id,  # Store ride_id for reference
                'value_b': 'ride_payment',
                'value_c': tran_id,
                'value_d': str(amount)
            }
            
            # Make request to SSLCommerz
            response = requests.post(
                self.config.SSLCOMMERZ_SANDBOX_URL,
                data=payment_data,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to initiate payment with SSLCommerz"
                )
            
            result = response.json()
            
            if result.get('status') == 'SUCCESS':
                return SSLCommerzResponse(
                    status=result['status'],
                    sessionkey=result.get('sessionkey'),
                    GatewayPageURL=result.get('GatewayPageURL'),
                    redirectGatewayURL=result.get('redirectGatewayURL'),
                    directPaymentURLBank=result.get('directPaymentURLBank'),
                    desc=result.get('desc')
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Payment initiation failed: {result.get('failedreason', 'Unknown error')}"
                )
                
        except requests.RequestException as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Network error: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Payment initiation error: {str(e)}"
            )
    
    def validate_payment(self, val_id: str, tran_id: str, amount: str) -> Dict:
        """Validate payment with SSLCommerz"""
        try:
            validation_data = {
                'val_id': val_id,
                'store_id': self.config.SSLCOMMERZ_STORE_ID,
                'store_passwd': self.config.SSLCOMMERZ_STORE_PASSWORD,
                'format': 'json'
            }
            
            response = requests.post(
                self.config.SSLCOMMERZ_VALIDATION_URL,
                data=validation_data
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to validate payment"
                )
            
            result = response.json()
            
            # Verify transaction details
            if (result.get('status') == 'VALID' and 
                result.get('tran_id') == tran_id and 
                float(result.get('amount', 0)) == float(amount)):
                return result
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Payment validation failed"
                )
                
        except requests.RequestException as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Network error during validation: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Payment validation error: {str(e)}"
            )