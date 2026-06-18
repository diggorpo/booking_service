from sqlalchemy.ext.asyncio import AsyncSession
from core.infrastructure.db.models.booking import Status

from fastapi import Depends, HTTPException, status

from api.api_v1.bookings.schemas import BookingResponseSchema
from api.deps.db_session import get_db_session
from core.infrastructure.db.repositories import BookingRepository


class AdminBookingService:
    def __init__(
        self,
        db_session: AsyncSession = Depends(get_db_session),
        repo: BookingRepository = Depends(BookingRepository),
    ):
        self.db_session = db_session
        self.repo = repo

    async def cancel_booking(
        self,
        booking_id: int,
    ) -> BookingResponseSchema:
        booking = await self.repo.get_by_id(self.db_session, booking_id, ["slot"])

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No such booking"
            )

        cancelled_booking = await self.repo.update(
            session=self.db_session,
            obj=booking,
            data={"status": Status.CANCELLED_BY_ADMIN},
        )
        await self.db_session.commit()
        return BookingResponseSchema.model_validate(cancelled_booking)

    async def get_many_bookings(self) -> list[BookingResponseSchema]:

        bookings = await self.repo.get_many(
            self.db_session, order_by="date", joins=["slot"]
        )

        return [BookingResponseSchema.model_validate(booking) for booking in bookings]
