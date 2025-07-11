from fastapi import FastAPI
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer
from auth import protected
from auth.router import router as auth_router
from users.router import router as user_router
from payments.router import router as payment_router
from drivers.routes.driverRoutes import driver_router
app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # Dummy for Swagger UI

app.include_router(protected.router, prefix="/api", dependencies=[Depends(oauth2_scheme)])
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(payment_router)
app.include_router(driver_router)

@app.get("/")
def read_root():
    return {"Hello": "World"}