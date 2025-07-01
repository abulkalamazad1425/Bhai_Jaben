from .supabase_config import supabase
from .schemas import UserLogin, UserSignup, DriverSignup


def signup_user(data: UserSignup):
    auth = supabase.auth.sign_up({
        "email": data.email,
        "password": data.password
    })

    if not auth.user:
        raise Exception("Signup failed")

    user_id = auth.user.id

    supabase.table("users").insert({
        "id": user_id,
        "name": data.name,
        "phone": data.phone,
        "role": data.role
    }).execute()

    return auth

def signup_driver(data: DriverSignup):
    auth = supabase.auth.sign_up({
        "email": data.email,
        "password": data.password
    })

    if not auth.user:
        raise Exception("Signup failed")

    user_id = auth.user.id

    supabase.table("users").insert({
        "id": user_id,
        "name": data.name,
        "phone": data.phone,
        "role": data.role
    }).execute()

    supabase.table("driver_profiles").insert({
        "user_id": user_id,
        "license": data.license,
        "vehicle_info": data.vehicle_info,
    }).execute()

    return auth


def login_user(data):
    return supabase.auth.sign_in_with_password({"email": data.email, "password": data.password})
