from typing import Type, TypeVar
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from api.deps.db_session import get_db_session
from core.infrastructure.db.repositories.base import SQLAlchemyBaseRepository

R = TypeVar("R", bound=SQLAlchemyBaseRepository)


def get_repository(repo_type: Type[R]):

    def dependency(session: AsyncSession = Depends(get_db_session)) -> R:
        return repo_type(session)  #

    return dependency
