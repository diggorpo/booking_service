from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.infrastructure.db.models.base import Base

if TYPE_CHECKING:
    from core.infrastructure.db.models.booking import Booking
    from core.infrastructure.db.models.role import Role


class User(Base):
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100))
    phone_number: Mapped[str] = mapped_column(String(20))
    password_hash: Mapped[bytes] = mapped_column()
    role_id: Mapped[int] = mapped_column(ForeignKey("roles.id"))

    role: Mapped["Role"] = relationship(back_populates="users")
    bookings: Mapped[list["Booking"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
