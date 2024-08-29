from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.types import DECIMAL

from app.database.base_db import Base

if TYPE_CHECKING:
    from app.database.models import OrderItem
    from app.database.models import User, Product


class Basket(Base):

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))

    user: Mapped["User"] = relationship(back_populates="basket")
    items: Mapped[list["BasketItem"]] = relationship(
        back_populates="basket", cascade="all, delete-orphan"
    )
    order_items: Mapped["OrderItem"] = relationship(back_populates="basket")

    def __str__(self):
        return f"Корзина: #{self.id}"


class BasketItem(Base):

    basket_id: Mapped[int] = mapped_column(ForeignKey("baskets.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int] = mapped_column(nullable=False, default=1)
    price: Mapped[DECIMAL] = mapped_column(Numeric(10, 2))

    basket: Mapped["Basket"] = relationship(back_populates="items")
    product: Mapped["Product"] = relationship(back_populates="items")

    __table_args__ = (
        UniqueConstraint("basket_id", "product_id", name="uq_task_user_permission"),
    )

    def __str__(self):
        return f"Продукт: #{self.product_id}"
