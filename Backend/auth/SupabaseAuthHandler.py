from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer, HTTPBearer
import jwt
import os
from .schemas import UserId
from .supabase_config import supabase

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # Supabase's token endpoint
security = HTTPBearer()

class SupabaseAuth:
    def __init__(self, supabase_client):
        '''
        self.secret = "lAyw4FC+Tou8CeSnGI9RdMxUbO0D3Gsp15qj0jlYqEL2o3UNHkAqBabt7B7HlMS5RSLW2+eICYgujGrWj4vxdg=="
        if not self.secret:
            raise RuntimeError("SUPABASE_JWT_SECRET not set")
        '''
        self.supabase = supabase_client

    def validate_token_format(self, token: str):
        parts = token.split('.')
        if len(parts) != 3:  # Proper JWT has 3 parts
            raise HTTPException(401, "Invalid token structure")
        return True

    def get_current_user(self, request: Request):
        token = request.cookies.get("access_token")
        if not token:
            raise HTTPException(401, "Not authenticated")
        
        try:
            # Verify the token is still valid
            user = self.supabase.auth.get_user(token)
            return user.user
        except Exception as e:
            raise HTTPException(401, f"Invalid token: {str(e)}")
# Initialize once
auth = SupabaseAuth(supabase)