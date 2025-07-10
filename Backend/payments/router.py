from fastapi import APIRouter, Request
from .schemas import PaymentRequest
from .service import initiate_payment

router = APIRouter(prefix="/payment", tags=["Payment"])

@router.post("/initiate")
def create_payment(data: PaymentRequest):
    return initiate_payment(data)

@router.post("/success")
async def payment_success(request: Request):
    form = await request.form()
    return {"status": "success", "data": dict(form)}

@router.post("/fail")
async def payment_fail(request: Request):
    form = await request.form()
    return {"status": "failed", "data": dict(form)}

@router.post("/cancel")
async def payment_cancel(request: Request):
    form = await request.form()
    return {"status": "cancelled", "data": dict(form)}
