from core.infrastructure.db.repositories.base import SQLAlchemyBaseRepository
from core.infrastructure.db.models.user import User


class UserRepository(SQLAlchemyBaseRepository):
    model = User
