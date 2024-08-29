from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, declared_attr, Mapped, mapped_column

from app.config import settings

engine = create_async_engine(settings.DB_URL)
session_factory = async_sessionmaker(engine)


class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return f"{cls.__name__.lower()}s"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
