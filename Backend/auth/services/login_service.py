from zope.interface import implementer
from .auth_service import ILoginService
from auth.schemas import UserLogin, UserBase, AuthResponse
from fastapi import Response, Request, HTTPException

@implementer(ILoginService)
class LoginService:
    def __init__(self, database_client):
        self.database = database_client

    def login_user(self, data: UserLogin):
        response = self.database.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password
        })
    
        return AuthResponse(
            user=UserBase(
                id=str(response.user.id),
                email=str(response.user.email),
                created_at=response.user.created_at
            ),
            access_token=response.session.access_token,
            refresh_token=response.session.refresh_token
        )

    def login_and_set_cookie(self, data: UserLogin, response: Response):
        login_response = self.login_user(data)
        response.set_cookie(
            key="access_token",
            value=login_response.access_token,
            httponly=True,
            secure=True,
            samesite='lax'
        )
        return login_response.user

    def get_current_user(self, request: Request):
        token = request.cookies.get("access_token")
        if not token:
            raise HTTPException(401, "Not authenticated")
        
        try:
            user = self.database.auth.get_user(token)
            return user.user.id
        except Exception as e:
            raise HTTPException(401, f"Invalid token: {str(e)}")