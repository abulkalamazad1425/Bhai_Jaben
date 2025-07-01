from fastapi import APIRouter
from .service import signup_user, login_user, signup_driver
from .schemas import UserLogin, UserSignup, DriverSignup

router = APIRouter(prefix='/auth', tags=['Authentication'])

@router.post("/signup/")
def sign_up(data: UserSignup):
    return signup_user(data)

@router.post("/signup/driver/")
def sign_up_driver(data: DriverSignup):
    return signup_driver(data)

@router.post("/login/")
def log(data: UserLogin):
    return login_user(data)
