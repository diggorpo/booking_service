import enum
from datetime import datetime, timezone, date
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, func, Date
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.infrastructure.db.models.base import Base

if TYPE_CHECKING:
    from core.infrastructure.db.models.slot import Slot
    from core.infrastructure.db.models.user import User


class Status(enum.Enum):
    BOOKED = "booked"
    CANCELLED_BY_USER = "cancelled_by_user"
    CANCELLED_BY_ADMIN = "cancelled_by_admin"
    NOT_VISITED = "not_visited"


class Booking(Base):
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    slot_id: Mapped[int] = mapped_column(ForeignKey("slots.id"))
    date: Mapped[date] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        server_default=func.now(),
    )
    status: Mapped[Status] = mapped_column(
        default=Status.BOOKED, server_default="BOOKED"
    )
    user: Mapped["User"] = relationship(back_populates="bookings")
    slot: Mapped["Slot"] = relationship(back_populates="bookings")
    __table_args__ = (
        Index(
            "idx_unique_active_booking_per_slot_date",
            "slot_id",
            "date",
            unique=True,
            postgresql_where=(status == Status.BOOKED.name),
            sqlite_where=(status == Status.BOOKED.name),
        ),
    )
