from datetime import time

from pydantic import BaseModel, ConfigDict


class BaseSlotSchema(BaseModel):
    start_time: time | None = None
    end_time: time | None = None


class Room(BaseModel):
    room_id: int


class SlotCreationResponseSchema(BaseSlotSchema):
    id: int

    room: Room


class SlotQueryParams(BaseSlotSchema):
    order_by: str = "id"


class SlotResponseSchema(BaseModel):
    start_time: time
    end_time: time
    room_id: int
    model_config = ConfigDict(from_attributes=True)
