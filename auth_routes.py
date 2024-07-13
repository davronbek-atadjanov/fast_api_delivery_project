from fastapi import APIRouter, status
from fastapi.exceptions import HTTPException
from models import User
from schemas import SignUpModel
from database import session, engine
from werkzeug.security import generate_password_hash, check_password_hash


auth_router = APIRouter(
    prefix='/auth'
)

session = session(bind=engine)

@auth_router.get('/')
async def welcome():
    return {'message': 'Bu signup sahifasi'}


@auth_router.post('/signup', status_code=status.HTTP_201_CREATED)
async def signup(user: SignUpModel):
    db_email = session.query(User).filter(User.email == user.email).first()
    if db_email is not None:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail="User with this email already exists")
    db_username = session.query(User).filter(User.username == user.username).first()
    if db_username is not None:
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                             detail="User with this username already exists")

    new_user = User(
        username=user.username,
        email=user.email,
        password=generate_password_hash(user.password),
        is_active=user.is_active,
        is_staff=user.is_staff,
    )

    session.add(new_user)
    session.commit()

    data = {
        "id": new_user.id,
        "username": new_user.username,
        "email": new_user.email,
        "is_staff": new_user.is_staff,
        "is_active": new_user.is_active
    }

    response_data = {
        "success": True,
        "status": 201,
        "message": "User is created successfully",
        "data": data
    }
    return response_data





