from fastapi import APIRouter, Depends, status

from api.api_v1.admin.bookings.service import AdminBookingService
from api.api_v1.bookings.schemas import BookingResponseSchema


router = APIRouter(tags=["Admin Booking"])


@router.get(
    "", response_model=list[BookingResponseSchema], status_code=status.HTTP_200_OK
)
async def get_all_bookings(service: AdminBookingService = Depends(AdminBookingService)):
    return await service.get_many_bookings()


@router.patch(
    "/{booking_id}/cancel",
    response_model=BookingResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def cancel_booking(
    booking_id: int, service: AdminBookingService = Depends(AdminBookingService)
):
    return await service.cancel_booking(booking_id)
