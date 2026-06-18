import pytest
from httpx import AsyncClient
from starlette import status


@pytest.mark.anyio
async def test_cancel_booking_success(auth_client: AsyncClient, seed_bookings):

    response = await auth_client.patch("/api/v1/bookings/1/cancel")

    assert response.status_code == status.HTTP_200_OK


@pytest.mark.anyio
async def test_cancel_booking_wrong_user(auth_client: AsyncClient, seed_bookings):

    response = await auth_client.patch("/api/v1/bookings/2/cancel")

    assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.anyio
async def test_cancel_fantom_booking(auth_client: AsyncClient, seed_bookings):

    response = await auth_client.patch("/api/v1/bookings/10/cancel")

    assert response.status_code == status.HTTP_404_NOT_FOUND
