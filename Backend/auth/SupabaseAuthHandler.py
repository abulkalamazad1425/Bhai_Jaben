from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
import os
from .schemas import UserId

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # Supabase's token endpoint

class SupabaseAuth:
    def __init__(self):
        self.secret = "lAyw4FC+Tou8CeSnGI9RdMxUbO0D3Gsp15qj0jlYqEL2o3UNHkAqBabt7B7HlMS5RSLW2+eICYgujGrWj4vxdg=="
        if not self.secret:
            raise RuntimeError("SUPABASE_JWT_SECRET not set")

    def get_current_user(self, token: str = Depends(oauth2_scheme)):
        try:
            payload = jwt.decode(token, self.secret, algorithms=["HS256"])
            return  UserId(id=payload["sub"])
                
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired"
            )
        except jwt.PyJWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )

# Initialize once
auth = SupabaseAuth()