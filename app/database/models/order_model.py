from enum import Enum
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, String, Enum as SQLEnum, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.types import DECIMAL

from app.database.base_db import Base

if TYPE_CHECKING:
    from app.database.models import User, Basket, Product


class PaymentType(Enum):
    Card = "card"
    PayPal = "paypal"
    Cash = "cash"


class Order(Base):

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    total_price: Mapped[DECIMAL] = mapped_column(Numeric(10, 2))
    status: Mapped[str] = mapped_column(String, default="pending")
    payment_method: Mapped[PaymentType] = mapped_column(
        SQLEnum(PaymentType), nullable=False
    )

    user: Mapped["User"] = relationship(back_populates="order")
    order_items: Mapped[list["OrderItem"]] = relationship(back_populates="order")

    def __str__(self):
        return f"Заказ: #{self.id}"


class OrderItem(Base):

    basket_id: Mapped[int] = mapped_column(ForeignKey("baskets.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    quantity: Mapped[int] = mapped_column(nullable=False, default=1)
    price: Mapped[DECIMAL] = mapped_column(Numeric(10, 2))

    basket: Mapped["Basket"] = relationship(back_populates="order_items")
    product: Mapped["Product"] = relationship(back_populates="order_items")
    order: Mapped["Order"] = relationship(back_populates="order_items")

    def __str__(self):
        return f"Продукт: #{self.product_id}"
