from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from core.infrastructure.db.models.booking import Status

from fastapi import Depends, HTTPException, status

from api.api_v1.bookings.schemas import BookingResponseSchema
from api.deps.db_session import get_db_session
from core.infrastructure.db.repositories import BookingRepository


class BookingService:
    def __init__(
        self,
        db_session: AsyncSession = Depends(get_db_session),
        repo: BookingRepository = Depends(BookingRepository),
    ):
        self.db_session = db_session
        self.repo = repo

    async def create_booking(
        self, slot_id: int, date: date, user_id: int
    ) -> BookingResponseSchema:
        try:
            booking = await self.repo.create(
                self.db_session,
                {"slot_id": slot_id, "user_id": user_id, "date": date},
                refresh_attributes=["slot"],
            )
            await self.db_session.commit()
            return BookingResponseSchema.model_validate(booking)
        except IntegrityError:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Slot is already booked or doesn't exist",
            )

    async def cancel_booking(
        self,
        booking_id: int,
        user_id: int,
    ) -> BookingResponseSchema:
        booking = await self.repo.get_by_id(self.db_session, booking_id, ["slot"])

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No such booking"
            )
        if booking.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not accessed to the booking",
            )

        cancelled_booking = await self.repo.update(
            session=self.db_session,
            obj=booking,
            data={"status": Status.CANCELLED_BY_USER},
        )
        await self.db_session.commit()
        return BookingResponseSchema.model_validate(cancelled_booking)

    async def get_many_bookings(self, user_id) -> list[BookingResponseSchema]:

        bookings = await self.repo.get_user_bookings_with_slots(
            self.db_session, **{"user_id": user_id}
        )

        return [BookingResponseSchema.model_validate(booking) for booking in bookings]
