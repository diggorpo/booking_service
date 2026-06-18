from typing import Annotated
from fastapi import APIRouter, Depends, status


from .schemas import (
    DayAvailabilitySchema,
    SlotAvailabilityQuery,
)
from .service import SlotService

router = APIRouter(tags=["Slots"])


@router.get(
    "/availability",
    response_model=list[DayAvailabilitySchema],
    status_code=status.HTTP_200_OK,
)
async def get_available_slots(
    params: Annotated[SlotAvailabilityQuery, Depends()],
    service: SlotService = Depends(SlotService),
):
    return await service.get_free_slots(params)
