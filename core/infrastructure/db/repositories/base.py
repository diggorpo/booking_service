from abc import ABC, abstractmethod
from typing import Any, Generic, Sequence, TypeVar
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from sqlalchemy import asc, select

T = TypeVar("T")


class BaseRepository(ABC, Generic[T]):
    @abstractmethod
    async def create(
        self,
        data: dict,
        refresh_attributes: list[str] | None = None,
    ) -> T | None:
        raise NotImplementedError

    @abstractmethod
    async def find_one(self, **filter_by: Any) -> T | None:
        raise NotImplementedError

    @abstractmethod
    async def get_by_id(self, id: int, joins: list[str] | None = None) -> T | None:
        raise NotImplementedError

    @abstractmethod
    async def get_many(
        self, order_by, joins: list[str] | None = None, **filter_by: Any
    ) -> Sequence[T]:
        raise NotImplementedError

    @abstractmethod
    async def update(
        self,
        data: dict,
        id: int | None = None,
        joins: list[str] | None = None,
        obj: T | None = None,
    ) -> T | None:
        raise NotImplementedError


class SQLAlchemyBaseRepository(BaseRepository[T], Generic[T]):
    model: type[T]

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        data: dict,
        refresh_attributes: list[str] | None = None,
    ) -> T:

        obj = self.model(**data)

        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj, refresh_attributes)
        return obj

    async def find_one(self, **filter_by: Any) -> T | None:

        stmt = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(stmt)
        return result.scalars().one_or_none()

    async def get_by_id(self, id: int, joins: list[str] | None = None) -> T | None:

        options = []

        if joins:
            for relation_name in joins:
                try:
                    relation_attr = getattr(self.model, relation_name)

                    options.append(joinedload(relation_attr))
                except AttributeError:
                    raise AttributeError(
                        f"Модель {self.model.__name__} не имеет связи с именем '{relation_name}'"
                    )

        return await self.session.get(self.model, id, options=options)

    async def get_many(
        self,
        order_by: str = "id",
        joins: list[str] | None = None,
        **filter_by: Any,
    ) -> Sequence[T]:

        options = []

        if joins:
            for relation_name in joins:
                try:
                    relation_attr = getattr(self.model, relation_name)

                    options.append(joinedload(relation_attr))
                except AttributeError:
                    raise AttributeError(
                        f"Модель {self.model.__name__} не имеет связи с именем '{relation_name}'"
                    )

        stmt = (
            select(self.model)
            .filter_by(**filter_by)
            .order_by(asc(getattr(self.model, order_by)))
        )
        if options:
            stmt = stmt.options(*options)

        result = await self.session.execute(stmt)

        return result.scalars().all()

    async def update(
        self,
        data: dict,
        id: int | None = None,
        joins: list[str] | None = None,
        obj: T | None = None,
    ) -> T | None:

        if not obj and id:
            obj = await self.get_by_id(id, joins=joins)

        if not obj:
            return None

        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)

        await self.session.flush()

        if joins:
            await self.session.refresh(obj, attribute_names=joins)

        return obj
