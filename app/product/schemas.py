from pydantic import BaseModel
from decimal import Decimal


class ProductRead(BaseModel):
    id: int
    name: str
    description: str
    price: Decimal
    quantity: int
    category_id: int
