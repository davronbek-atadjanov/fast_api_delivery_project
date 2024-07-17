from fastapi import APIRouter, Depends, status
from models import User, Product
from schemas import ProductModel
from fastapi_jwt_auth import AuthJWT
from database import session, engine
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import HTTPException

product_router =  APIRouter(
    prefix='/product'
)

session = session(bind=engine)

@product_router.post('/create', status_code=status.HTTP_201_CREATED)
async def create_product(product: ProductModel, Authorize: AuthJWT=Depends()):
    """
        Create a new product endpoint
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token access invalid")

    current_user = Authorize.get_jwt_subject()
    db_user = session.query(User).filter(User.username == current_user).first()

    if db_user.is_staff:
        new_product = Product(
            name=product.name,
            price=product.price
        )
        session.add(new_product)
        session.commit()

        data = {
            "success": True,
            "code": 201,
            "message": "Product is create successfully",
            "data": {
                "id": new_product.id,
                "name": new_product.name,
                "price": new_product.price
            }
        }

        return jsonable_encoder(data)
    else:
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only Admin can add new product")


@product_router.get('/list', status_code=status.HTTP_200_OK)
async def get_product_list(Authorize: AuthJWT=Depends()):
    """
        Product list endpoint
     """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token access invalid")

    current_user = Authorize.get_jwt_subject()
    db_user = session.query(User).filter(User.username == current_user).first()

    if db_user.is_staff:
        products = session.query(Product).all()
        custom_data = [
            {
                "id": product.id,
                "name": product.name,
                "price": product.price
            }
            for product in products
        ]

        return jsonable_encoder(custom_data)
    else:
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only Admin can list product")


@product_router.get('/{id}', status_code=status.HTTP_200_OK)
async def get_product_by_id(id: int, Authorize: AuthJWT=Depends()):
    """
           Product get by id endpoint
        """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token access invalid")

    current_user = Authorize.get_jwt_subject()
    db_user = session.query(User).filter(User.username == current_user).first()

    if db_user.is_staff:
        product = session.query(Product).filter(Product.id == id).first()

        if product:
            data = {
                "id": product.id,
                "name": product.name,
                "price": product.price
            }

            return jsonable_encoder(data)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Product with {id} ID not found")

    else:
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only admin can by id product")


@product_router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_product_by_id(id: int, Authorize: AuthJWT=Depends()):
    """
        This endpoint Product delete
    """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")

    username = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == username).first()

    if current_user.is_staff:
        product = session.query(Product).filter(Product.id == id).first()
        if product:
            session.delete(product)
            session.commit()
            data = {
                "success": True,
                "code": 204,
                "message": f"Product with ID {id} has been deleted"
            }
            return jsonable_encoder(data)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"This product ID {id} is not found")
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only Admin is allowed to delete product")


@product_router.put('/{id}/update', status_code=status.HTTP_200_OK)
async def update_product_by_id(id: int, update_data: ProductModel, Authorize: AuthJWT=Depends()):
    """
          This endpoint Product update
      """
    try:
        Authorize.jwt_required()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")

    username = Authorize.get_jwt_subject()
    current_user = session.query(User).filter(User.username == username).first()

    if current_user.is_staff:
        product = session.query(Product).filter(Product.id == id).first()
        if product:
             # update product
            for key, value in update_data.dict(exclude_unset=True).items():
                setattr(product, key, value)
            # product.price = update_data.price
            session.commit()
            data = {
                "success": True,
                "code": 200,
                "message": f"{id} id Product update",
                "data": {
                    "id": product.id,
                    "name": product.name,
                    "price": product.price
                }
            }
            return jsonable_encoder(data)
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"This product ID {id} is not found")
    else:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only Admin is allowed to update product")