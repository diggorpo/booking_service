import pytest
from httpx import AsyncClient
from starlette import status


@pytest.mark.anyio
async def test_create_booking_success(auth_client: AsyncClient, seed_slots):

    response = await auth_client.post(
        "/api/v1/bookings/1?date=2026-07-18", json={"slot_id": 1, "date": "2026-07-17"}
    )

    assert response.status_code == status.HTTP_201_CREATED
