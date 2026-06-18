from core.infrastructure.db.repositories.base import SQLAlchemyBaseRepository
from core.infrastructure.db.models import Booking


class BookingRepository(SQLAlchemyBaseRepository[Booking]):
    model = Booking
