from unittest.mock import AsyncMock, MagicMock
from datetime import date, datetime, timezone

import pytest
from fastapi import HTTPException

from api.api_v1.bookings.admin.service import AdminBookingService
from api.api_v1.bookings.schemas import BookingResponseSchema
from core.infrastructure.db.repositories.bookings import BookingRepository
from core.infrastructure.db.models.booking import Status


@pytest.fixture
def mock_db_session():
    return AsyncMock()


@pytest.fixture
def mock_booking_repo():
    return AsyncMock(spec=BookingRepository)


@pytest.fixture
def admin_booking_service(mock_db_session, mock_booking_repo):
    service = AdminBookingService.__new__(AdminBookingService)
    service.db_session = mock_db_session
    service.repo = mock_booking_repo
    return service


@pytest.fixture
def mock_booking():
    booking = MagicMock()
    booking.id = 1
    booking.date = date(2026, 6, 20)
    booking.created_at = datetime(2026, 6, 19, 12, 0, 0, tzinfo=timezone.utc)
    booking.updated_at = datetime(2026, 6, 19, 12, 0, 0, tzinfo=timezone.utc)
    booking.status = Status.BOOKED
    booking.user_id = 2
    booking.slot = MagicMock()
    booking.slot.start_time = "09:00:00"
    booking.slot.end_time = "11:00:00"
    booking.slot.room_id = 1
    return booking


class TestAdminCancelBooking:
    @pytest.mark.anyio
    async def test_admin_cancel_booking_success(
        self, admin_booking_service, mock_booking_repo, mock_db_session, mock_booking
    ):
        mock_booking_repo.get_by_id.return_value = mock_booking
        mock_booking_repo.update.return_value = mock_booking

        result = await admin_booking_service.admin_cancel_booking(booking_id=1)

        assert isinstance(result, BookingResponseSchema)
        assert result.id == 1
        mock_booking_repo.get_by_id.assert_awaited_once_with(1, ["slot"])
        mock_booking_repo.update.assert_awaited_once_with(
            obj=mock_booking, data={"status": Status.CANCELLED_BY_ADMIN}
        )
        mock_db_session.commit.assert_awaited_once()

    @pytest.mark.anyio
    async def test_admin_cancel_booking_not_found(
        self, admin_booking_service, mock_booking_repo
    ):
        mock_booking_repo.get_by_id.return_value = None

        with pytest.raises(HTTPException) as exc_info:
            await admin_booking_service.admin_cancel_booking(booking_id=999)

        assert exc_info.value.status_code == 404
        assert exc_info.value.detail == "No such booking"
        mock_booking_repo.get_by_id.assert_awaited_once_with(999, ["slot"])


class TestAdminGetManyBookings:
    @pytest.mark.anyio
    async def test_admin_get_many_bookings_success(
        self, admin_booking_service, mock_booking_repo, mock_booking
    ):
        mock_booking_repo.get_many.return_value = [mock_booking]

        result = await admin_booking_service.admin_get_many_bookings()

        assert len(result) == 1
        assert isinstance(result[0], BookingResponseSchema)
        mock_booking_repo.get_many.assert_awaited_once_with(
            order_by="date", joins=["slot"]
        )

    @pytest.mark.anyio
    async def test_admin_get_many_bookings_empty(
        self, admin_booking_service, mock_booking_repo
    ):
        mock_booking_repo.get_many.return_value = []

        result = await admin_booking_service.admin_get_many_bookings()

        assert result == []
        mock_booking_repo.get_many.assert_awaited_once_with(
            order_by="date", joins=["slot"]
        )
