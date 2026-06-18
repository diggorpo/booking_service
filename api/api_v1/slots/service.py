from datetime import timedelta
from typing import Any
from fastapi import Depends
from api.deps.get_repo import get_repository
from core.infrastructure.db.repositories import SlotRepository, BookingRepository

from .schemas import SlotAvailabilityQuery, DayAvailabilitySchema, FreeSlotSchema


class SlotService:
    def __init__(
        self,
        slot_repo: SlotRepository = Depends(get_repository(SlotRepository)),
        booking_repo: BookingRepository = Depends(get_repository(BookingRepository)),
    ):
        self.slot_repo = slot_repo
        self.booking_repo = booking_repo

    async def get_free_slots(
        self, params: SlotAvailabilityQuery
    ) -> list[DayAvailabilitySchema]:

        slot_filters: dict[str, Any] = {}
        if params.room_id is not None:
            slot_filters["room_id"] = params.room_id

        slots = await self.slot_repo.get_many(**slot_filters)
        if not slots:
            return []

        slot_ids = [s.id for s in slots]

        active_bookings = await self.booking_repo.get_active_bookings_for_slots(
            slot_ids=slot_ids, start_date=params.start_date, end_date=params.end_date
        )
        booked_map = {(b.date, b.slot_id) for b in active_bookings}

        result = []
        current_date = params.start_date
        while current_date <= params.end_date:
            free_slots_for_day = []
            for slot in slots:
                if (current_date, slot.id) not in booked_map:
                    free_slots_for_day.append(
                        FreeSlotSchema(
                            id=slot.id,
                            start_time=slot.start_time,
                            end_time=slot.end_time,
                        )
                    )

            result.append(
                DayAvailabilitySchema(date=current_date, free_slots=free_slots_for_day)
            )
            current_date += timedelta(days=1)

        return result
