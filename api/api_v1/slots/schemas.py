from datetime import date, datetime, time, timedelta, timezone

from pydantic import BaseModel, ConfigDict, Field


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


def get_today() -> date:
    return datetime.now(timezone.utc).date()


def get_two_weeks_later() -> date:
    return get_today() + timedelta(days=14)


class SlotAvailabilityQuery(BaseModel):
    room_id: int | None = None
    start_date: date = Field(
        default_factory=get_today,
        description="Начальная дата (ГГГГ-ММ-ДД)",
    )
    end_date: date = Field(
        default_factory=get_two_weeks_later,
        description="Конечная дата (ГГГГ-ММ-ДД)",
    )


class FreeSlotSchema(BaseModel):
    id: int
    start_time: time
    end_time: time


class DayAvailabilitySchema(BaseModel):
    date: date
    free_slots: list[FreeSlotSchema]
