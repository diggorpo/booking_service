from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status

from api.api_v1.slots.schemas import SlotResponseSchema
from api.deps.db_session import get_db_session
from core.infrastructure.db.repositories import SlotRepository
from core.config import settings


class SlotService:
    def __init__(
        self,
        db_session: AsyncSession = Depends(get_db_session),
        repo: SlotRepository = Depends(SlotRepository),
    ):
        self.db_session = db_session
        self.repo = repo

    async def get_many_slots(self, params) -> list[SlotResponseSchema]:
        slots = await self.repo.get_many(
            self.db_session, **params.model_dump(exclude_unset=True)
        )

        return [SlotResponseSchema.model_validate(slot) for slot in slots]
