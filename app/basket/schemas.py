from pydantic import BaseModel

from decimal import Decimal


class BasketCreate(BaseModel):
    user_id: int


class BasketRead(BaseModel):
    id: int
    user_id: int


class BasketItemRead(BaseModel):
    id: int
    basket_id: int
    product_id: int
    quantity: int
    price: Decimal


class BasketItemMiniRead(BaseModel):
    product_name: str
    quantity: int
    price: Decimal
