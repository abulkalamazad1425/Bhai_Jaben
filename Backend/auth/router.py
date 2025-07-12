from fastapi import APIRouter, Depends, Response
#from fastapi.security import 
from .supabase_config import supabase
from .service import AuthService
from .schemas import UserLogin, UserSignup, DriverSignup, UserId
from .SupabaseAuthHandler import auth

router = APIRouter(prefix='/auth', tags=['Authentication'])

auth_service=AuthService(supabase)

@router.post("/signup/")
def sign_up(data: UserSignup):
    return auth_service.signup_user(data)

@router.post("/signup/driver/")
def sign_up_driver(data: DriverSignup):
    return auth_service.signup_driver(data)

@router.post("/login/")
def log(data: UserLogin, response: Response):
    return auth_service.login_and_set_cookie(data, response)
