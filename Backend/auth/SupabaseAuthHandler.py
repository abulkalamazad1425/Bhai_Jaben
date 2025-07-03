from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
import os

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="", auto_error=False)  # Supabase's token endpoint

class SupabaseAuth:
    def __init__(self):
        self.secret = "lAyw4FC+Tou8CeSnGI9RdMxUbO0D3Gsp15qj0jlYqEL2o3UNHkAqBabt7B7HlMS5RSLW2+eICYgujGrWj4vxdg=="
        if not self.secret:
            raise RuntimeError("SUPABASE_JWT_SECRET not set")

    async def get_current_user(self, token: str = Depends(oauth2_scheme)) -> dict:
        try:
            payload = jwt.decode(token, self.secret, algorithms=["HS256"])
            return {
                "id": payload["sub"],
                "email": payload.get("email"),
                "role": payload.get("role", "authenticated")
            }
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