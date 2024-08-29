from sqlalchemy import select, insert, delete, update
from sqlalchemy.exc import SQLAlchemyError

from app.database.base_db import session_factory
from app.exception.base_exceptions import DataBaseError


class BaseDAO:
    model = None

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        async with session_factory() as session:
            query = select(cls.model.__table__.columns).filter_by(**filter_by)
            result = await session.execute(query)
            return result.mappings().one_or_none()

    @classmethod
    async def find_all(cls, **filter_by):
        async with session_factory() as session:
            query = select(cls.model.__table__.columns).filter_by(**filter_by)
            result = await session.execute(query)
            return result.mappings().all()

    @classmethod
    async def add(cls, **data):
        query = insert(cls.model).values(**data).returning(cls.model.id)
        async with session_factory() as session:
            result = await session.execute(query)
            await session.commit()
            return result.mappings().first()

    @classmethod
    async def update(cls, id, **data):
        query = (
            update(cls.model).values(**data).filter_by(id=id).returning(cls.model.id)
        )
        async with session_factory() as session:
            result = await session.execute(query)
            await session.commit()
            return result.mappings().first()

    @classmethod
    async def delete(cls, **filter_by):
        async with session_factory() as session:
            query = delete(cls.model).filter_by(**filter_by)
            await session.execute(query)
            await session.commit()

    # @classmethod
    # async def update(cls, **data):
    #     query = update(cls.model).where()
    #     async with session_factory() as session:
