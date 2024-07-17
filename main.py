from fastapi import FastAPI
from pydantic import BaseModel
from auth_routes import auth_router
from order_routes import order_router
from product_routes import product_router
from fastapi_jwt_auth import AuthJWT
from schemas import  Login
app = FastAPI()


class Settings(BaseModel):
    authjwt_secret_key: str = 'e9aea1f6d5aff0651e1e39cb64419353ceaf7fc57d978afe9b83299bd3a641fd'

@AuthJWT.load_config
def get_config():
    return Settings()


app.include_router(auth_router)
app.include_router(order_router)
app.include_router(product_router)

@app.get("/")
async def root():
    return {"message": "Bu asosiy sahifa"}


