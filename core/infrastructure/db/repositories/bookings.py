from datetime import date
from typing import Sequence

from sqlalchemy import select
from core.infrastructure.db.models.booking import Status
from core.infrastructure.db.repositories.base import SQLAlchemyBaseRepository
from core.infrastructure.db.models import Booking


class BookingRepository(SQLAlchemyBaseRepository[Booking]):
    model = Booking

    async def get_active_bookings_for_slots(
        self, slot_ids: list[int], start_date: date, end_date: date
    ) -> Sequence[Booking]:
        stmt = select(self.model).where(
            self.model.slot_id.in_(slot_ids),
            self.model.date >= start_date,
            self.model.date <= end_date,
            self.model.status == Status.BOOKED,
        )
        result = await self.session.execute(stmt)
        return result.scalars().all()
