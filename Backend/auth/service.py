from .schemas import UserLogin, UserSignup, DriverSignup

class AuthService:
    def __init__(self, supabase_client):
        self.supabase = supabase_client

    def signup_user(self, data: UserSignup):
        auth = self.supabase.auth.sign_up({
            "email": data.email,
            "password": data.password
        })

        if not auth.user:
            raise Exception("Signup failed")

        user_id = auth.user.id

        self.supabase.table("users").insert({
            "id": user_id,
            "name": data.name,
            "phone": data.phone,
            "role": data.role,
            "email": data.email
        }).execute()

        return auth

    def signup_driver(self, data: DriverSignup):
        auth = self.supabase.auth.sign_up({
            "email": data.email,
            "password": data.password
        })

        if not auth.user:
            raise Exception("Signup failed")

        user_id = auth.user.id

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

        return auth

    def login_user(self, data: UserLogin):
        return self.supabase.auth.sign_in_with_password({
            "email": data.email,
            "password": data.password
        })
