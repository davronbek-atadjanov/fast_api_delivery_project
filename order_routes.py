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
        product_id=order.product_id
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
            "product": {
                "id": new_order.product.id,
                "name": new_order.product.name,
                "price": new_order.product.price
            },
            "quantity": new_order.quantity,
            "order_statuses": new_order.order_status.value,
            "total_price": new_order.quantity * new_order.product.price
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
                "product": {
                    "id": order.product.id,
                    "name": order.product.name,
                    "price": order.product.price
                },
                "quantity": order.quantity,
                "order_statuses": order.order_status.value,
                "total_price": order.quantity * order.product.price

            } for order in orders
        ]
        return jsonable_encoder(custom_data)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only SuperAdmin can see all orders")


@order_router.get('/{id}', status_code=status.HTTP_200_OK)
async def get_order_by_id(id: int, Authorize: AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    current_user = Authorize.get_jwt_subject()
    db_user = session.query(User).filter(User.username == current_user).first()

    if db_user.is_staff:
        order = session.query(Order).filter(Order.id == id).first()
        if order:
            response = {
                "id": order.id,
                "user": {
                    "id": order.user.id,
                    "username": order.user.username,
                    "email": order.user.email
                },
                "product": {
                    "id": order.product.id,
                    "name": order.product.name,
                    "price": order.product.price
                },
                "quantity": order.quantity,
                "order_statuses": order.order_status.value,
                "total_price": order.quantity * order.product.price
            }
            return jsonable_encoder(response)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Order with {id} ID is not found")
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only SuperAdmin is allowed to this request")

@order_router.get('/user/orders', status_code=status.HTTP_200_OK)
async def get_user_order_list(Authorize: AuthJWT=Depends()):
    """
        Get a request user's orders
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")
    username = Authorize.get_jwt_subject()
    db_user = session.query(User).filter(User.username == username).first()
    response = [
        {
            "id": order.id,
            "user": {
                "id": order.user.id,
                "username": order.user.username,
                "email": order.user.email
            },
            "product": {
                "id": order.product.id,
                "name": order.product.name,
                "price": order.product.price
            },
            "quantity": order.quantity,
            "order_statuses": order.order_status.value,
            "total_price": order.quantity * order.product.price
        }
        for order in db_user.orders
    ]
    return jsonable_encoder(response)



@order_router.get('/user/order/{id}', status_code=status.HTTP_200_OK)
async def get_user_order_by_id(id: int, Authorize: AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")

    username = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == username).first()
    order = session.query(Order).filter(Order.id == id, Order.user == current_user).first()
    if order:
        order_data = {
            "id": order.id,
            "user": {
                "id": order.user.id,
                "username": order.user.username,
                "email": order.user.email
            },
            "product": {
                "id": order.product.id,
                "name": order.product.name,
                "price": order.product.price
            },
            "quantity": order.quantity,
            "order_statuses": order.order_status,
            "total_price": order.quantity * order.product.price
        }
        return jsonable_encoder(order_data)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No order with this {id} ID")


@order_router.put('/{id}/update', status_code=status.HTTP_202_ACCEPTED)
async def update_order(id: int, order: OrderModel, Authorize: AuthJWT=Depends()):
    """
        Update user order by fields: quantity and product id
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")

    username = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == username).first()

    order_to_update = session.query(Order).filter(Order.id == id, Order.user == current_user).first()

    if not order_to_update:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can not update others users's update")

    order_to_update.quantity = order.quantity
    order_to_update.product_id = order.product_id
    session.commit()

    custom_data = {
        "success": True,
        "code": 202,
        "message": "You order Update",
        "data": {
            "id": order.id,
            "quantity": order.quantity,
            "product": order.product_id,
            "order_statuses": order.order_statuses
        }
    }
    return jsonable_encoder(custom_data)

@order_router.patch('/{id}/update-status')
async def update_order_status(id: int, order: OrderStatusModel, Authorize: AuthJWT=Depends()):
    """
           Update status user order
       """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")

    username = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == username).first()
    if current_user.is_staff:
        order_to_update = session.query(Order).filter(Order.id == id).first()
        order_to_update.order_status = order.order_statuses
        session.commit()

        custom_response = {
            "success": True,
            "code": 202,
            "message": "User order statuses update",
            "data": {
                "id": order_to_update.id,
                "order_statuses": order_to_update.order_status
            }
        }
        return jsonable_encoder(custom_response)
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only SuperAdmin is allowed to this request")


@order_router.delete('/{id}/delete', status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(id: int, Authorize: AuthJWT=Depends()):
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")

    username = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == username).first()
    order = session.query(Order).filter(Order.id == id).first()
    if order.user != current_user:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Kechirasi, siz boshqa foydalanuvchilarni buyurtmalarini o'chira olmaysiz")

    if order.order_status != "PANDING":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Kechirasi, siz yo'lga chiqan va yetkazib berilgan buyurtmalarni o'chira olamysiz")
    session.delete(order)
    session.commit()

    custom_response = {
        "success": True,
        "code": 204,
        "message": "This order delete",
        "data": None
    }
    return jsonable_encoder(custom_response)
