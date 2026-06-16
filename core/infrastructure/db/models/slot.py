from datetime import time
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Time
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.infrastructure.db.models.base import Base

if TYPE_CHECKING:
    from core.infrastructure.db.models.booking import Booking
    from core.infrastructure.db.models.room import Room


class Slot(Base):
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"))
    start_time: Mapped[time] = mapped_column(Time(timezone=True))
    end_time: Mapped[time] = mapped_column(Time(timezone=True))

    room: Mapped["Room"] = relationship(back_populates="slots")
    bookings: Mapped[list["Booking"]] = relationship(
        back_populates="slot", cascade="all, delete-orphan"
    )
