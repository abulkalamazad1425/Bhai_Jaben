from fastapi import Header, HTTPException, Depends
from typing import Dict, Any, Optional
import jwt
import os
from jwt import PyJWTError

class JWTAuthHandler:
    def __init__(self, secret_key: str = None, algorithm: str = "HS256"):
        self.secret_key = secret_key 
        #or os.getenv("SUPABASE_JWT_SECRET")
        if not self.secret_key:
            raise ValueError("No JWT secret key provided")
        self.algorithm = algorithm

    async def get_current_user(
        self,
        authorization: str = Header(...,alias="Authorization"),
        verify_exp: bool = True,
        verify_iss: bool = False,
        issuer: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Dependency to get current user from JWT token
        
        Args:
            authorization: The Authorization header containing Bearer token
            verify_exp: Whether to verify token expiration
            verify_iss: Whether to verify issuer claim
            issuer: Expected issuer if verify_iss is True
            
        Returns:
            Decoded JWT payload
            
        Raises:
            HTTPException: If token is invalid
        """
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail="Invalid token format. Expected 'Bearer <token>'"
            )

        token = authorization.split(" ")[1]
        
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm],
                options={
                    "verify_exp": verify_exp,
                    "verify_iss": verify_iss,
                },
                issuer=issuer if verify_iss else None
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except PyJWTError as e:
            raise HTTPException(status_code=401, detail=f"Invalid token: {str(e)}")

# Initialize with your Supabase secret
jwt_auth = JWTAuthHandler(
    secret_key="lAyw4FC+Tou8CeSnGI9RdMxUbO0D3Gsp15qj0jlYqEL2o3UNHkAqBabt7B7HlMS5RSLW2+eICYgujGrWj4vxdg=="
)