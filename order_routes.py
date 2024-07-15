from fastapi import APIRouter, Depends, status

import order_routes
from models import Order, User, Product
from schemas import OrderModel, OrderStatusModel
from fastapi_jwt_auth import AuthJWT
from database import session, engine
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException


order_router = APIRouter(
    prefix='/order'
)

session = session(bind=engine)


@order_router.get('/')
async def welcome(Autherize: AuthJWT=Depends()):
    try:
        Autherize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return {'message': 'Bu order sahifasi'}


@order_router.post('/make', status_code=status.HTTP_201_CREATED)
async def make_order(order: OrderModel, Authorize: AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    current_user = Authorize.get_jwt_subject()
    db_user = session.query(User).filter(User.username == current_user).first()

    new_order = Order(
        quantity=order.quantity,
        # product=order.product_id
    )
    new_order.user = db_user
    session.add(new_order)
    session.commit()
    response = {
        "success": True,
        "code": 201,
        "message": "Order created successfully",
        "data": {
            "id": new_order.id,
            "quantity": new_order.quantity,
            "order_statuses": new_order.order_status
        }

    }
    return jsonable_encoder(response)


@order_router.get('/list')
async def list_all_order(Authorize: AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    current_user = Authorize.get_jwt_subject()
    db_user = session.query(User).filter(User.username == current_user).first()

    if db_user.is_staff:
        orders = session.query(Order).all()
        custom_data = [
            {
                "id": order.id,
                "user": {
                    "id": order.user.id,
                    "username": order.user.username,
                    "email": order.user.email
                },
                "product_id": order.product_id,
                "quantity": order.quantity,
                "order_statuses": order.order_status.value,

            } for order in orders
        ]
        return jsonable_encoder(custom_data)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only SuperAdmin can see all orders")


@order_router.get('/{id}')
async def get_order_by_id(id: int, Authorize: AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    current_user = Authorize.get_jwt_subject()
    db_user = session.query(User).filter(User.username == current_user).first()

    if db_user.is_staff:
        order = session.query(Order).filter(Order.id == id).first()
        response = {
                "id": order.id,
                "user": {
                    "id": order.user.id,
                    "username": order.user.username,
                    "email": order.user.email
                },
                "product_id": order.product_id,
                "quantity": order.quantity,
                "order_statuses": order.order_status.value,

            }
        return jsonable_encoder(response)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only SuperAdmin is allowed to this request")


