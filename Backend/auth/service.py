from .schemas import UserLogin, UserSignup, DriverSignup, AuthResponse, UserBase
from fastapi import Response

class AuthService:
    def __init__(self, supabase_client):
        self.supabase = supabase_client

    def signup_user(self, data: UserSignup):
        response = self.supabase.auth.sign_up({
            "email": data.email,
            "password": data.password
        })

        if not response.user:
            raise Exception("Signup failed")

        user_id = response.user.id

        self.supabase.table("users").insert({
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
            access_token=response.user.access_token,
            refresh_token=response.user.refresh_token
        )

    def signup_driver(self, data: DriverSignup):
        response = self.supabase.auth.sign_up({
            "email": data.email,
            "password": data.password
        })

        if not response.user:
            raise Exception("Signup failed")

        user_id = response.user.id

        self.supabase.table("users").insert({
            "id": user_id,
            "name": data.name,
            "phone": data.phone,
            "role": data.role,
            "email": data.email
        }).execute()

        self.supabase.table("driver_profiles").insert({
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
            access_token=response.user.access_token,
            refresh_token=response.user.refresh_token
        )

    def login_user(self, data: UserLogin):
        response = self.supabase.auth.sign_in_with_password({
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
        login_response=self.login_user(data)
        response.set_cookie(
            key="access_token",
            value=login_response.access_token,
            httponly=True,
            secure=True,
            samesite='lax'
        )
        return login_response.user
        