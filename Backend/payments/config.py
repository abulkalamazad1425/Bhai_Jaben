import os
from typing import Dict

class PaymentConfig:
    
    # SSLCommerz Sandbox Configuration
    SSLCOMMERZ_STORE_ID = os.getenv("SSLCZ_STORE_ID", "testbox")
    SSLCOMMERZ_STORE_PASSWORD = os.getenv("SSLCZ_STORE_PASSWD", "qwerty")
    SSLCOMMERZ_SANDBOX_URL = "https://sandbox.sslcommerz.com/gwprocess/v4/api.php"
    SSLCOMMERZ_VALIDATION_URL = "https://sandbox.sslcommerz.com/validator/api/validationserverAPI.php"
    
    # Production URLs (uncomment when going live)
    # SSLCOMMERZ_PRODUCTION_URL = "https://securepay.sslcommerz.com/gwprocess/v4/api.php"
    # SSLCOMMERZ_PRODUCTION_VALIDATION_URL = "https://securepay.sslcommerz.com/validator/api/validationserverAPI.php"
    
    # Application URLs
    BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8002")
    
    @classmethod
    def get_callback_urls(cls) -> Dict[str, str]:
        return {
            "success_url": f"{cls.BASE_URL}/payment/success",
            "fail_url": f"{cls.BASE_URL}/payment/failed",
            "cancel_url": f"{cls.BASE_URL}/payment/cancel",
            "ipn_url": f"{cls.BASE_URL}/payment/ipn"  # Instant Payment Notification
        }