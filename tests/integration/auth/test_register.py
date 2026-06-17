import pytest
from httpx import AsyncClient
from starlette import status


@pytest.mark.anyio
async def test_register_user_success(client: AsyncClient, seed_roles):
    payload = {
        "first_name": "Yaroslav",
        "last_name": "Nikolaev",
        "email": "yaroslav@example.com",
        "phone_number": "+79991112233",
        "password": "securepassword123",
    }

    response = await client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == status.HTTP_201_CREATED

    data = response.json()
    assert data["email"] == payload["email"]
    assert data["first_name"] == payload["first_name"]

    assert "id" in data
    assert isinstance(data["id"], int)
    assert data["id"] > 0


@pytest.mark.anyio
async def test_register_user_invalid_email(client: AsyncClient, seed_roles):
    payload = {
        "first_name": "Yaroslav",
        "last_name": "Nikolaev",
        "email": "invalid-email-format",
        "phone_number": "+79991112233",
        "role": "user",
        "password": "securepassword123",
    }

    response = await client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    errors = response.json()["detail"]
    assert len(errors) > 0
    assert errors[0]["loc"] == ["body", "email"]


@pytest.mark.anyio
async def test_register_user_duplicate_email(client: AsyncClient, seed_roles):
    payload = {
        "first_name": "Yaroslav",
        "last_name": "Nikolaev",
        "email": "duplicate@example.com",
        "phone_number": "+79991112233",
        "role": "user",
        "password": "securepassword123",
    }

    first_response = await client.post("/api/v1/auth/register", json=payload)
    assert first_response.status_code == status.HTTP_201_CREATED

    payload["first_name"] = "Ivan"
    second_response = await client.post("/api/v1/auth/register", json=payload)

    assert second_response.status_code == status.HTTP_409_CONFLICT
