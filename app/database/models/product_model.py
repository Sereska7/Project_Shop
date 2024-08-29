from typing import TYPE_CHECKING

from sqlalchemy import String, Numeric, ForeignKey
from sqlalchemy.types import DECIMAL
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.database.base_db import Base

if TYPE_CHECKING:
    from app.database.models import Category, BasketItem, OrderItem


class Product(Base):

    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(255))
    price: Mapped[DECIMAL] = mapped_column(Numeric(10, 2))
    quantity: Mapped[int]
    category_id: Mapped[int] = mapped_column(ForeignKey("categorys.id"), nullable=False)

    category: Mapped["Category"] = relationship(back_populates="product")
    items: Mapped["BasketItem"] = relationship(back_populates="product")
    order_items: Mapped["OrderItem"] = relationship(back_populates="product")

    def __str__(self):
        return f"{self.name}"
