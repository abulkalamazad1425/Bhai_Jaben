from fastapi import APIRouter, Depends, Response, Request
from fastapi.responses import JSONResponse
#from fastapi.security import 
from .supabase_config import supabase
from .service import AuthService
from .schemas import UserLogin, UserSignup, DriverSignup, UserId, TokenResponse
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

@router.get("/test/")
def test(request: Request):
    # Get access token from cookies
    access_token = request.cookies.get("access_token")
    
    if access_token:
        return TokenResponse(
            access_token=access_token
        )
    else:
        return JSONResponse(
            content={"error": "Access token not found"},
            status_code=404
        )

@router.get("/currentuser/")
def get_current_user(request: Request):
    return auth_service.get_current_user(request)
