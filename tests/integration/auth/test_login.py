import pytest
from httpx import AsyncClient
from starlette import status


@pytest.mark.anyio
async def test_login_user_success(client: AsyncClient, seed_roles):
    register_payload = {
        "first_name": "Yaroslav",
        "last_name": "Nikolaev",
        "email": "yaroslav@example.com",
        "phone_number": "+79991112233",
        "role": "user",
        "password": "securepassword123",
    }
    await client.post("/api/v1/auth/register", json=register_payload)

    login_payload = {"email": "yaroslav@example.com", "password": "securepassword123"}
    response = await client.post("/api/v1/auth/login", json=login_payload)

    assert response.status_code == status.HTTP_200_OK

    assert "Authorization" in response.cookies
    assert response.cookies["Authorization"] is not None


@pytest.mark.anyio
async def test_login_user_wrong_password(client: AsyncClient, seed_roles):

    register_payload = {
        "first_name": "Yaroslav",
        "last_name": "Nikolaev",
        "email": "yaroslav@example.com",
        "phone_number": "+79991112233",
        "role": "user",
        "password": "securepassword123",
    }
    await client.post("/api/v1/auth/register", json=register_payload)

    login_payload = {
        "email": "yaroslav@example.com",
        "password": "wrong_password_here",
    }
    response = await client.post("/api/v1/auth/login", json=login_payload)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.anyio
async def test_login_user_nonexistent_email(client: AsyncClient, seed_roles):
    login_payload = {
        "email": "nonexistent@example.com",
        "password": "any_password_here",
    }
    response = await client.post("/api/v1/auth/login", json=login_payload)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
