from fastapi import APIRouter, Depends, Response, Request
from fastapi.responses import JSONResponse
from .services.login_service import LoginService
from .services.register_service import RegisterService
from .database_config import DatabaseConfig
from .schemas import UserLogin, UserSignup, DriverSignup, UserId, TokenResponse

router = APIRouter(prefix='/auth', tags=['Authentication'])


database_client=DatabaseConfig().get_client()
login_service=LoginService(database_client)
register_service=RegisterService(database_client)

@router.post("/signup/")
def sign_up(data: UserSignup, response: Response):
    return register_service.signup_and_set_cookie(data,response)

@router.post("/signup/driver/")
def sign_up_driver(data: DriverSignup, response: Response):
    return register_service.signup_driver_and_set_cookie(data,response)

@router.post("/login/")
def log(data: UserLogin, response: Response):
    return login_service.login_and_set_cookie(data, response)

@router.get("/test/")
def test(request: Request):
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
    return login_service.get_current_user(request)
