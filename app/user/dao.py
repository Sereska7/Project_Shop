from sqlalchemy import insert
from sqlalchemy.exc import SQLAlchemyError

from app.database.base_db import session_factory
from app.database.base_dao import BaseDAO
from app.database.models import User
from app.exception.base_exceptions import DataBaseError


class UserDAO(BaseDAO):
    model = User

    @classmethod
    async def add(cls, **data):
        try:
            query = (
                insert(cls.model)
                .values(**data)
                .returning(cls.model.id, cls.model.email)
            )
            async with session_factory() as session:
                result = await session.execute(query)
                await session.commit()
                return result.mappings().first()
        except SQLAlchemyError:
            DataBaseError("Database Except: Cannot insert data into table")
            return None
