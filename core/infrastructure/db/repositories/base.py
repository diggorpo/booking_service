from abc import ABC, abstractmethod
from typing import Any, Generic, Sequence, TypeVar

from sqlalchemy import asc, select

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    @abstractmethod
    async def create(self, session, data: dict) -> T | None:
        raise NotImplementedError

    @abstractmethod
    async def find_one(self, session, **filter_by: Any) -> T | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, session, id: int) -> T | None:
        raise NotImplementedError

    @abstractmethod
    async def update_by_id(self, session, id: int) -> T | None:
        raise NotImplementedError

    @abstractmethod
    async def get_many(self, session, order_by, **filter_by: Any) -> Sequence[T]:
        raise NotImplementedError


class SQLAlchemyBaseRepository(BaseRepository[T], Generic[T]):
    model: type[T]

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

    async def get_many(
        self, session, order_by: str = "id", **filter_by: Any
    ) -> Sequence[T]:

        stmt = select(self.model).order_by(asc(getattr(self.model, order_by)))

        result = await self.session.execute(stmt)

        return result.scalars().all()
