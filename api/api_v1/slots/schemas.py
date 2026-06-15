from datetime import datetime

from pydantic import BaseModel, ConfigDict


class BaseSlotSchema(BaseModel):
    start_time: datetime | None = None
    end_time: datetime | None = None


class Room(BaseModel):
    room_id: int


class SlotCreationResponseSchema(BaseSlotSchema):
    id: int

    room: Room


class SlotQueryParams(BaseSlotSchema):
    order_by: str = "id"


class SlotResponseSchema(BaseModel):
    start_time: datetime
    end_time: datetime
    room_id: int
    is_available: bool = True
    model_config = ConfigDict(from_attributes=True)
