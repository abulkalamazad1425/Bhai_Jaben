from fastapi import FastAPI
from auth.router import router as auth_router
from users.router import router as user_router

app = FastAPI()
app.include_router(auth_router)
app.include_router(user_router)

@app.get("/")
def read_root():
    return {"Hello": "World"}