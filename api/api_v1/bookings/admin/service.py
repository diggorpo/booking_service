from api.api_v1.bookings.service import BookingService
from core.infrastructure.db.models.booking import Status

from fastapi import HTTPException, status

from api.api_v1.bookings.schemas import BookingResponseSchema


class AdminBookingService(BookingService):
    async def admin_cancel_booking(
        self,
        booking_id: int,
    ) -> BookingResponseSchema:
        booking = await self.repo.get_by_id(booking_id, ["slot"])

        if not booking:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="No such booking"
            )

        cancelled_booking = await self.repo.update(
            obj=booking,
            data={"status": Status.CANCELLED_BY_ADMIN},
        )
        await self.db_session.commit()
        return BookingResponseSchema.model_validate(cancelled_booking)

    async def admin_get_many_bookings(self) -> list[BookingResponseSchema]:

        bookings = await self.repo.get_many(order_by="date", joins=["slot"])

        return [BookingResponseSchema.model_validate(booking) for booking in bookings]
