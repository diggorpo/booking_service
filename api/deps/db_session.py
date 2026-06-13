from core.infrastructure.db.db_helper import db_helper
from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:

    async with db_helper.session_factory() as session:
        yield session
