from datetime import datetime

from pydantic import BaseModel

class Room(BaseModel):
    room_id: int

class SlotInfo(BaseModel):
    start_time: datetime
    end_time: datetime
    room: Room


class BookingResponseSchema(BaseModel):
    id: int
    slot: SlotInfo
    created_at: datetime
    updated_at: datetime
    status: str


