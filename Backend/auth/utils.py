from fastapi import Header, HTTPException, Depends
import jwt

SUPABASE_JWT_SECRET = "lAyw4FC+Tou8CeSnGI9RdMxUbO0D3Gsp15qj0jlYqEL2o3UNHkAqBabt7B7HlMS5RSLW2+eICYgujGrWj4vxdg=="  

def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid token format")

    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SUPABASE_JWT_SECRET, algorithms=["HS256"])
        return payload  
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
