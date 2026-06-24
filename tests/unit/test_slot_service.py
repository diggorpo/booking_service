from unittest.mock import AsyncMock, MagicMock
from datetime import date, time, timezone

import pytest

from api.api_v1.slots.service import SlotService
from api.api_v1.slots.schemas import (
    SlotAvailabilityQuery,
)
from core.infrastructure.db.repositories import SlotRepository, BookingRepository


@pytest.fixture
def mock_slot_repo():
    return AsyncMock(spec=SlotRepository)


@pytest.fixture
def mock_booking_repo():
    return AsyncMock(spec=BookingRepository)


@pytest.fixture
def slot_service(mock_slot_repo, mock_booking_repo):
    service = SlotService.__new__(SlotService)
    service.slot_repo = mock_slot_repo
    service.booking_repo = mock_booking_repo
    return service


@pytest.fixture
def mock_slots():
    slot1 = MagicMock()
    slot1.id = 1
    slot1.start_time = time(9, 0, tzinfo=timezone.utc)
    slot1.end_time = time(11, 0, tzinfo=timezone.utc)

    slot2 = MagicMock()
    slot2.id = 2
    slot2.start_time = time(11, 0, tzinfo=timezone.utc)
    slot2.end_time = time(13, 0, tzinfo=timezone.utc)

    return [slot1, slot2]


@pytest.fixture
def query_params():
    return SlotAvailabilityQuery(
        start_date=date(2026, 6, 20),
        end_date=date(2026, 6, 20),
    )


class TestGetFreeSlots:
    @pytest.mark.anyio
    async def test_no_slots(self, slot_service, mock_slot_repo, query_params):
        mock_slot_repo.get_many.return_value = []

        result = await slot_service.get_free_slots(query_params)

        assert result == []
        mock_slot_repo.get_many.assert_awaited_once()

    @pytest.mark.anyio
    async def test_all_slots_free(
        self, slot_service, mock_slot_repo, mock_booking_repo, mock_slots, query_params
    ):
        mock_slot_repo.get_many.return_value = mock_slots
        mock_booking_repo.get_active_bookings_for_slots.return_value = []

        result = await slot_service.get_free_slots(query_params)

        assert len(result) == 1
        day_avail = result[0]
        assert day_avail.date == date(2026, 6, 20)
        assert len(day_avail.free_slots) == 2
        assert day_avail.free_slots[0].id == 1
        assert day_avail.free_slots[1].id == 2

    @pytest.mark.anyio
    async def test_some_slots_booked(
        self, slot_service, mock_slot_repo, mock_booking_repo, mock_slots, query_params
    ):
        mock_slot_repo.get_many.return_value = mock_slots

        mock_booking = MagicMock()
        mock_booking.date = date(2026, 6, 20)
        mock_booking.slot_id = 1
        mock_booking_repo.get_active_bookings_for_slots.return_value = [mock_booking]

        result = await slot_service.get_free_slots(query_params)

        assert len(result) == 1
        assert len(result[0].free_slots) == 1
        assert result[0].free_slots[0].id == 2

    @pytest.mark.anyio
    async def test_all_slots_booked(
        self, slot_service, mock_slot_repo, mock_booking_repo, mock_slots, query_params
    ):
        mock_slot_repo.get_many.return_value = mock_slots

        mock_booking1 = MagicMock()
        mock_booking1.date = date(2026, 6, 20)
        mock_booking1.slot_id = 1

        mock_booking2 = MagicMock()
        mock_booking2.date = date(2026, 6, 20)
        mock_booking2.slot_id = 2

        mock_booking_repo.get_active_bookings_for_slots.return_value = [
            mock_booking1,
            mock_booking2,
        ]

        result = await slot_service.get_free_slots(query_params)

        assert len(result) == 1
        assert len(result[0].free_slots) == 0

    @pytest.mark.anyio
    async def test_filter_by_room_id(
        self, slot_service, mock_slot_repo, mock_booking_repo, mock_slots, query_params
    ):
        query_params.room_id = 1
        mock_slot_repo.get_many.return_value = mock_slots
        mock_booking_repo.get_active_bookings_for_slots.return_value = []

        result = await slot_service.get_free_slots(query_params)

        assert len(result) == 1
        mock_slot_repo.get_many.assert_awaited_once_with(room_id=1)
        mock_booking_repo.get_active_bookings_for_slots.assert_awaited_once_with(
            slot_ids=[1, 2],
            start_date=date(2026, 6, 20),
            end_date=date(2026, 6, 20),
        )

    @pytest.mark.anyio
    async def test_multiple_days(
        self, slot_service, mock_slot_repo, mock_booking_repo, mock_slots
    ):
        query = SlotAvailabilityQuery(
            start_date=date(2026, 6, 20),
            end_date=date(2026, 6, 21),
        )
        mock_slot_repo.get_many.return_value = mock_slots
        mock_booking_repo.get_active_bookings_for_slots.return_value = []

        result = await slot_service.get_free_slots(query)

        assert len(result) == 2
        assert result[0].date == date(2026, 6, 20)
        assert result[1].date == date(2026, 6, 21)
        for day in result:
            assert len(day.free_slots) == 2
