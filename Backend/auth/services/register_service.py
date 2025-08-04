from zope.interface import implementer
from .auth_service import IRegisterService
from auth.schemas import UserSignup, DriverSignup, AuthResponse, UserBase
from fastapi import Request, Response

@implementer(IRegisterService)
class RegisterService:
    def __init__(self, database_client):
        self.database = database_client

    def signup_user(self, data: UserSignup):
        response = self.database.auth.sign_up({
            "email": data.email,
            "password": data.password
        })

        if not response.user:
            raise Exception("Signup failed")

        user_id = response.user.id

        self.database.table("users").insert({
            "id": user_id,
            "name": data.name,
            "phone": data.phone,
            "role": data.role,
            "email": data.email
        }).execute()

        return AuthResponse(
            user=UserBase(
                id=str(response.user.id),
                email=response.user.email,
                created_at=response.user.created_at
            ),
            access_token=response.session.access_token,
            refresh_token=response.session.refresh_token
        )

    def signup_and_set_cookie(self, data: UserSignup, response: Response):
        signup_response = self.signup_user(data)
        response.set_cookie(
            key="access_token",
            value=signup_response.access_token,
            httponly=True,
            secure=True,
            samesite='lax'
        )
        return signup_response.user

    def signup_driver(self, data: DriverSignup):
        response = self.database.auth.sign_up({
            "email": data.email,
            "password": data.password
        })

        if not response.user:
            raise Exception("Signup failed")

        user_id = response.user.id

        self.database.table("users").insert({
            "id": user_id,
            "name": data.name,
            "phone": data.phone,
            "role": data.role,
            "email": data.email
        }).execute()

        self.database.table("driver_profiles").insert({
            "user_id": user_id,
            "license": data.license,
            "vehicle_info": data.vehicle_info,
        }).execute()

        return AuthResponse(
            user=UserBase(
                id=str(response.user.id),
                email=response.user.email,
                created_at=response.user.created_at
            ),
            access_token=response.session.access_token,
            refresh_token=response.session.refresh_token
        )

    def signup_driver_and_set_cookie(self, data: DriverSignup, response: Response):
        signup_response = self.signup_driver(data)
        response.set_cookie(
            key="access_token",
            value=signup_response.access_token,
            httponly=True,
            secure=True,
            samesite='lax'
        )
        return signup_response.user