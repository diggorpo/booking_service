from datetime import date, datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from api.deps.get_repo import get_repository
from core.infrastructure.db.models.booking import Status

from fastapi import Depends, HTTPException, status

from api.api_v1.bookings.schemas import BookingResponseSchema
from api.deps.db_session import get_db_session
from core.infrastructure.db.repositories import BookingRepository, SlotRepository


class BookingService:
    def __init__(
        self,
        db_session: AsyncSession = Depends(get_db_session),
        repo: BookingRepository = Depends(get_repository(BookingRepository)),
        slot_repo: SlotRepository = Depends(get_repository(SlotRepository)),
    ):
        self.db_session = db_session
        self.repo = repo
        self.slot_repo = slot_repo

    async def create_booking(
        self, slot_id: int, booking_date: date, user_id: int
    ) -> BookingResponseSchema:
        # Проверка, что дата не в прошлом
        if booking_date < datetime.now(timezone.utc).date():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot book a slot in the past",
            )

        # Проверка существования слота
        slot = await self.slot_repo.get_by_id(slot_id)
        if not slot:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Slot not found",
            )

        try:
            booking = await self.repo.create(
                {"slot_id": slot_id, "user_id": user_id, "date": booking_date},
                refresh_attributes=["slot"],
            )
            await self.db_session.commit()
            return BookingResponseSchema.model_validate(booking)
        except IntegrityError:
            await self.db_session.rollback()
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Slot is already booked",
            )

    async def cancel_booking(
        self,
        booking_id: int,
        user_id: int,
    ) -> BookingResponseSchema:
        booking = await self.repo.get_by_id(booking_id, ["slot"])

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No such booking"
            )
        if booking.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not accessed to the booking",
            )
        if booking.status != Status.BOOKED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Booking is already cancelled",
            )

        cancelled_booking = await self.repo.update(
            obj=booking,
            data={"status": Status.CANCELLED_BY_USER},
        )
        await self.db_session.commit()
        return BookingResponseSchema.model_validate(cancelled_booking)

    async def get_many_bookings(self, user_id) -> list[BookingResponseSchema]:

        bookings = await self.repo.get_many(
            joins=["slot"],
            **{"user_id": user_id},
        )

        return [BookingResponseSchema.model_validate(booking) for booking in bookings]
