from datetime import datetime, date

from pydantic import BaseModel, ConfigDict

from api.api_v1.slots.schemas import SlotResponseSchema


class Room(BaseModel):
    room_id: int


class BookingCreateQueryParams(BaseModel):
    slot_id: int
    date: date


class BookingResponseSchema(BaseModel):
    id: int
    date: date
    created_at: datetime
    updated_at: datetime
    status: str
    slot: SlotResponseSchema

    model_config = ConfigDict(from_attributes=True)
