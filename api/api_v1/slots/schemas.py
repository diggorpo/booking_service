from datetime import datetime

from pydantic import BaseModel

class Room(BaseModel):
    room_id: int

class SlotCreationResponseSchema(BaseModel):
    id: int
    start_time: datetime
    end_time: datetime
    room: Room


