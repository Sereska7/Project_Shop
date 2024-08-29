from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.database.base_db import Base

if TYPE_CHECKING:
    from app.database.models import Product


class Category(Base):

    name: Mapped[str] = mapped_column(String(60))

    product: Mapped["Product"] = relationship(
        back_populates="category", cascade="all, delete-orphan"
    )

    def __str__(self):
        return f"{self.name}"
