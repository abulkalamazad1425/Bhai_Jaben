from fastapi import APIRouter
from .service import signup_user, login_user
from .schemas import UserLogin, UserSignup

router = APIRouter(prefix='/auth', tags=['Authentication'])

@router.post("/signup/")
def sign_up(data: UserSignup):
    return signup_user(data)

@router.post("/login/")
def log(data: UserLogin):
    return login_user(data)
