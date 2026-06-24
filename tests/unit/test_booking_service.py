from unittest.mock import AsyncMock, MagicMock
from datetime import date, datetime, timezone

import pytest
from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError

from api.api_v1.bookings.service import BookingService
from api.api_v1.bookings.schemas import BookingResponseSchema
from core.infrastructure.db.repositories.bookings import BookingRepository
from core.infrastructure.db.repositories.slots import SlotRepository
from core.infrastructure.db.models.booking import Status


@pytest.fixture
def mock_db_session():
    return AsyncMock()


@pytest.fixture
def mock_booking_repo():
    return AsyncMock(spec=BookingRepository)


@pytest.fixture
def mock_slot_repo():
    return AsyncMock(spec=SlotRepository)


@pytest.fixture
def booking_service(mock_db_session, mock_booking_repo, mock_slot_repo):
    service = BookingService.__new__(BookingService)
    service.db_session = mock_db_session
    service.repo = mock_booking_repo
    service.slot_repo = mock_slot_repo
    return service


@pytest.fixture
def mock_booking():
    booking = MagicMock()
    booking.id = 1
    booking.date = date(2026, 7, 20)
    booking.created_at = datetime(2026, 6, 19, 12, 0, 0, tzinfo=timezone.utc)
    booking.updated_at = datetime(2026, 6, 19, 12, 0, 0, tzinfo=timezone.utc)
    booking.status = Status.BOOKED
    booking.user_id = 2
    booking.slot = MagicMock()
    booking.slot.start_time = "09:00:00"
    booking.slot.end_time = "11:00:00"
    booking.slot.room_id = 1
    return booking


class TestCreateBooking:
    @pytest.mark.anyio
    async def test_create_booking_success(
        self, booking_service, mock_booking_repo, mock_db_session, mock_booking
    ):
        mock_booking_repo.create.return_value = mock_booking

        result = await booking_service.create_booking(
            slot_id=1, booking_date=date(2026, 7, 20), user_id=2
        )

        assert isinstance(result, BookingResponseSchema)
        assert result.id == 1
        assert result.date == date(2026, 7, 20)
        mock_booking_repo.create.assert_awaited_once_with(
            {"slot_id": 1, "user_id": 2, "date": date(2026, 7, 20)},
            refresh_attributes=["slot"],
        )
        mock_db_session.commit.assert_awaited_once()

    @pytest.mark.anyio
    async def test_create_booking_slot_not_found(self, booking_service, mock_slot_repo):
        mock_slot_repo.get_by_id.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await booking_service.create_booking(
                slot_id=999, booking_date=date(2026, 7, 20), user_id=2
            )

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "Slot not found"
        mock_slot_repo.get_by_id.assert_awaited_once_with(999)

    @pytest.mark.anyio
    async def test_create_booking_past_date(self, booking_service, mock_slot_repo):
        mock_slot_repo.get_by_id.return_value = MagicMock()

        with pytest.raises(HTTPException) as exc_info:
            await booking_service.create_booking(
                slot_id=1, booking_date=date(2020, 1, 1), user_id=2
            )

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Cannot book a slot in the past"

    @pytest.mark.anyio
    async def test_create_booking_integrity_error(
        self, booking_service, mock_booking_repo, mock_db_session, mock_slot_repo
    ):
        mock_slot_repo.get_by_id.return_value = MagicMock()
        mock_booking_repo.create.side_effect = IntegrityError("", "", Exception(""))

        with pytest.raises(HTTPException) as exc_info:
            await booking_service.create_booking(
                slot_id=999, booking_date=date(2026, 7, 20), user_id=2
            )

        assert exc_info.value.status_code == 409
        assert exc_info.value.detail == "Slot is already booked"
        mock_db_session.rollback.assert_awaited_once()
        mock_db_session.commit.assert_not_awaited()


class TestCancelBooking:
    @pytest.mark.anyio
    async def test_cancel_booking_success(
        self, booking_service, mock_booking_repo, mock_db_session, mock_booking
    ):
        mock_booking_repo.get_by_id.return_value = mock_booking
        mock_booking_repo.update.return_value = mock_booking

        result = await booking_service.cancel_booking(booking_id=1, user_id=2)

        assert isinstance(result, BookingResponseSchema)
        mock_booking_repo.get_by_id.assert_awaited_once_with(1, ["slot"])
        mock_booking_repo.update.assert_awaited_once_with(
            obj=mock_booking, data={"status": Status.CANCELLED_BY_USER}
        )
        mock_db_session.commit.assert_awaited_once()

    @pytest.mark.anyio
    async def test_cancel_booking_not_found(self, booking_service, mock_booking_repo):
        mock_booking_repo.get_by_id.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await booking_service.cancel_booking(booking_id=999, user_id=2)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "No such booking"

    @pytest.mark.anyio
    async def test_cancel_booking_forbidden(
        self, booking_service, mock_booking_repo, mock_booking
    ):
        mock_booking_repo.get_by_id.return_value = mock_booking

        with pytest.raises(HTTPException) as exc_info:
            await booking_service.cancel_booking(booking_id=1, user_id=999)

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "Not accessed to the booking"

    @pytest.mark.anyio
    async def test_cancel_already_cancelled_booking(
        self, booking_service, mock_booking_repo, mock_booking
    ):
        mock_booking.status = Status.CANCELLED_BY_USER
        mock_booking_repo.get_by_id.return_value = mock_booking

        with pytest.raises(HTTPException) as exc_info:
            await booking_service.cancel_booking(booking_id=1, user_id=2)

        assert exc_info.value.status_code == 400
        assert exc_info.value.detail == "Booking is already cancelled"


class TestGetManyBookings:
    @pytest.mark.anyio
    async def test_get_many_bookings_success(
        self, booking_service, mock_booking_repo, mock_booking
    ):
        mock_booking_repo.get_many.return_value = [mock_booking]

        result = await booking_service.get_many_bookings(user_id=2)

        assert len(result) == 1
        assert isinstance(result[0], BookingResponseSchema)
        mock_booking_repo.get_many.assert_awaited_once_with(joins=["slot"], user_id=2)

    @pytest.mark.anyio
    async def test_get_many_bookings_empty(self, booking_service, mock_booking_repo):
        mock_booking_repo.get_many.return_value = []

        result = await booking_service.get_many_bookings(user_id=999)

        assert result == []
