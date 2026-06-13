from abc import ABC, abstractmethod
from typing import Any, Generic, TypeVar

from sqlalchemy import select

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    @abstractmethod
    async def create(self, data: dict) -> T | None:
        raise NotImplementedError

    @abstractmethod
    async def find_one(self, **filter_by: Any) -> T | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, id: int) -> T | None:
        raise NotImplementedError


class SQLAlchemyBaseRepository(BaseRepository):
    model: type[T] | None = None

    async def create(self, session, data: dict) -> T:

        obj = self.model(**data)

        session.add(obj)
        session.flush()
        return obj

    async def find_one(self, session, **filter_by: Any) -> T | None:

        stmt = select(self.model).filter_by(**filter_by)
        result = await session.execute(stmt)
        return result.scalars().one_or_none()

    async def get_by_id(self, session, id: int) -> T | None:

        return await session.get(self.model, id)
