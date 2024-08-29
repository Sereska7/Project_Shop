from typing import TYPE_CHECKING

from sqlalchemy.orm import relationship, Mapped

from app.database.base_db import Base

if TYPE_CHECKING:
    from app.database.models import Basket, Order


class User(Base):

    email: Mapped[str]
    hash_password: Mapped[str]

    basket: Mapped["Basket"] = relationship(back_populates="user")
    order: Mapped[list["Order"]] = relationship(back_populates="user")

    def __str__(self):
        return f"Пользователь: {self.email}"
