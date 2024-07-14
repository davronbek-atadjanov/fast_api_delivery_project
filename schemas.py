from pydantic import BaseModel
from typing import Optional


class SignUpModel(BaseModel):
    id: Optional[int]
    username: str
    email: str
    password: str
    is_staff: Optional[bool]
    is_active: Optional[bool]

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "username": "Davronbek",
                "email": "davronbek@gmail.com",
                "password": "Davronbek45454",
                "is_staff": False,
                "is_active": True
            }
        }



class Login(BaseModel):
    username_or_email: str
    password: str