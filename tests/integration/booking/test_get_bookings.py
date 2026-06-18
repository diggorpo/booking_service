import pytest
from httpx import AsyncClient
from starlette import status


@pytest.mark.anyio
async def test_get_bookings(auth_client: AsyncClient, seed_bookings):
    response = await auth_client.get("/api/v1/bookings/")

    assert response.status_code == status.HTTP_200_OK

    data = response.json()
    assert isinstance(data, list)

    assert len(data) == 1

    booking = data[0]
    assert booking["id"] == 1

    assert booking["date"] == "2026-06-20"

    assert "slot" in booking
    assert "09:00:00" in booking["slot"]["start_time"]
