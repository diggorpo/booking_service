from typing import Sequence
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from core.infrastructure.db.repositories.base import SQLAlchemyBaseRepository
from core.infrastructure.db.models import Booking


class BookingRepository(SQLAlchemyBaseRepository[Booking]):
    model = Booking

    async def get_user_bookings_with_slots(
        self, session, user_id: int
    ) -> Sequence[Booking]:
        stmt = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .options(joinedload(self.model.slot))
        )
        result = await session.execute(stmt)
        return result.scalars().all()
