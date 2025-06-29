from fastapi import APIRouter
from .service import signup_user, login_user

router = APIRouter(prefix='/auth', tags=['Authentication'])

@router.post("/signup/")
def signup(email: str, password: str):
    return signup_user(email, password)

def log(email: str, password: str):
    return login_user(email, password)
