from fastapi import APIRouter, status

from .schemas import SlotCreationResponseSchema

router = APIRouter(tags=["Bookings"])


@router.post(
    "/create",
    response_model=SlotCreationResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_slot():
    pass


@router.delete(
    "/delete/{slot_id}",
    status_code=status.HTTP_202_ACCEPTED,
)
def change_booking_status():
    pass
