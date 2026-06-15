from typing import Annotated
from fastapi import APIRouter, Depends


from .schemas import SlotQueryParams, SlotResponseSchema
from .service import SlotService

router = APIRouter(tags=["Slots"])


@router.get("", response_model=list[SlotResponseSchema])
async def show_slots(
    params: Annotated[SlotQueryParams, Depends()],
    service: SlotService = Depends(SlotService),
):

    return await service.get_many_slots(params)
