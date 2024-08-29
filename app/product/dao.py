from sqlalchemy import select

from app.database.base_dao import BaseDAO
from app.database.base_db import session_factory
from app.database.models import Product


class ProductDAO(BaseDAO):
    model = Product

    @classmethod
    async def find_all_products(cls, limit: int = 5, offset: int = 0):
        async with session_factory() as session:
            query = select(cls.model.__table__.columns).limit(limit).offset(offset)
            result = await session.execute(query)
            return result.mappings().all()
