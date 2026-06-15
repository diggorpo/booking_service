from core.infrastructure.db.repositories.base import SQLAlchemyBaseRepository
from core.infrastructure.db.models import Slot


class SlotRepository(SQLAlchemyBaseRepository[Slot]):
    model = Slot
