from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.models.base import Base

if TYPE_CHECKING:
    from core.models.role import Role


class Permission(Base):
    name: Mapped[str] = mapped_column(String(50), unique=True)
    roles: Mapped[list["Role"]] = relationship(
        secondary="roles_permissions", back_populates="permissions"
    )
