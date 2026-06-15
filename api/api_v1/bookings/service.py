from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status

from api.deps.db_session import get_db_session
from core.infrastructure.db.repositories import BookingRepository
from core.config import settings


class BookingService:
    def __init__(
        self,
        db_session: AsyncSession = Depends(get_db_session),
        booking_repo: BookingRepository = Depends(BookingRepository),
    ):
        self.db_session = db_session
        self.booking_repo = booking_repo
