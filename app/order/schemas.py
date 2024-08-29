from decimal import Decimal
from enum import Enum

from pydantic import BaseModel


class OrderRead(BaseModel):
    user_id: int
    total_price: int
    status: str
    payment_method: str
