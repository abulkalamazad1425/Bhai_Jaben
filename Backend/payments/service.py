import os
from sslcommerz_lib import SSLCOMMERZ
from dotenv import load_dotenv
from uuid import uuid4

load_dotenv()

store_id = os.getenv("SSLCZ_STORE_ID")
print("Store ID:", store_id)
store_pass = os.getenv("SSLCZ_STORE_PASSWD")
base_url = os.getenv("BASE_URL")
def initiate_payment(data):
    sslcz = SSLCOMMERZ({
        'store_id': store_id,
        'store_pass': store_pass,
        'issandbox': True
    })

    transaction_id = str(uuid4())

    post_body = {}
    post_body['total_amount'] = data.amount
    post_body['currency'] = "BDT"
    post_body['tran_id'] = transaction_id
    post_body['success_url'] = f"{base_url}/payment/success"
    post_body['fail_url'] = f"{base_url}/payment/fail"
    post_body['cancel_url'] = f"{base_url}/payment/cancel"
    post_body['emi_option'] = 0
    post_body['cus_name'] = data.name
    post_body['cus_email'] = data.email
    post_body['cus_phone'] = data.phone
    post_body['cus_add1'] = "Dhaka"
    post_body['cus_city'] = "Dhaka"
    post_body['cus_country'] = "Bangladesh"
    post_body['shipping_method'] = "NO"
    post_body['product_name'] = "Ride Fare"
    post_body['product_category'] = "Ride"
    post_body['product_profile'] = "general"

    response = sslcz.createSession(post_body)
    print("SSLCommerz Response:", response)
    return {
        "payment_url": response.get('GatewayPageURL'),
        "transaction_id": transaction_id
    }
