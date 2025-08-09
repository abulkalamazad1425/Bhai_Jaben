from fastapi import FastAPI
import uvicorn
from auth.router import router as auth_router
from users.router import router as user_router
from drivers.router import router as driver_router
from rides.router import router as ride_router
from payments.router import router as payment_router

app = FastAPI()

app.include_router(auth_router)
app.include_router(user_router)
app.include_router(driver_router)
app.include_router(ride_router)
app.include_router(payment_router)

@app.get("/")
def read_root():
    return {"Message": "Application running in localhost"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8002, reload=True)
