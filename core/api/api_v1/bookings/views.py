from fastapi import APIRouter, status

from .schemas import BookingResponseSchema

router = APIRouter(tags=["Bookings"])


@router.post(
    "/book/{slot_id}",
    response_model=BookingResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
def book_slot():
    pass


@router.patch(
    "/change_status/{book_id}",
    response_model=BookingResponseSchema,
    status_code=status.HTTP_202_ACCEPTED,
)
def change_booking_status():
    pass
