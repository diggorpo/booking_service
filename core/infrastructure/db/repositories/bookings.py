from core.infrastructure.db.repositories.base import SQLAlchemyBaseRepository
from core.infrastructure.db.models import Booking
from sqlalchemy.exc import SQLAlchemyError


class BookingRepository(SQLAlchemyBaseRepository[Booking]):
    model = Booking

    async def create(self, session, data: dict) -> Booking:
        booking = self.model(**data)
        try:
            session.add(booking)
            await session.flush()

            await session.refresh(booking, attribute_names=["slot"])

            return booking
        except SQLAlchemyError as e:
            raise e
