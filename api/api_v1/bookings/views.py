from datetime import date
from typing import Annotated
from fastapi import APIRouter, Depends, status, Query

from api.api_v1.auth.schemas import UserResponseSchema
from api.deps.get_current_user import get_current_user
from core.infrastructure.db.models.booking import Status

from .schemas import BookingResponseSchema
from .service import BookingService

router = APIRouter(tags=["Bookings"])


@router.post(
    "/{slot_id}",
    response_model=BookingResponseSchema,
    status_code=status.HTTP_201_CREATED,
)
async def book_slot(
    slot_id: int,
    date: Annotated[
        date,
        Query(
            description="Target booking date in ISO 8601 format (YYYY-MM-DD)",
            example="2026-06-16",
        ),
    ],
    user: UserResponseSchema = Depends(get_current_user),
    service: BookingService = Depends(BookingService),
):
    return await service.create_booking(slot_id, date, user.id)


@router.patch(
    "/{booking_id}",
    response_model=BookingResponseSchema,
    status_code=status.HTTP_200_OK,
)
async def change_booking_status(
    booking_id: int,
    status: Annotated[Status, Query(description="New Status")],
    user: UserResponseSchema = Depends(get_current_user),
    service: BookingService = Depends(BookingService),
):
    return await service.change_status(
        user_id=user.id, booking_id=booking_id, book_status=status
    )
