from .supabase_config import supabase

def signup_user(email: str, password: str):
    return supabase.auth.sign_up({"email": email, "password": password})

def login_user(email: str, password: str):
    return supabase.auth.sign_in_with_password({"email": email, "password": password})
