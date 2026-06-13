from typing import TYPE_CHECKING

from sqlalchemy import Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import expression

from core.infrastructure.db.models.base import Base

if TYPE_CHECKING:
    from core.infrastructure.db.models.slot import Slot


class Room(Base):
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, server_default=expression.true()
    )
    slots: Mapped[list["Slot"]] = relationship(back_populates="room")
