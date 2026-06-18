from datetime import timedelta
import jwt
import pytest
from api.api_v1.auth.handler import auth_handler


async def create_token(expire_timedelta: timedelta):
    token, _ = await auth_handler.encode_jwt(
        {"user_id": 1}, expire_timedelta=expire_timedelta
    )
    return token


@pytest.mark.anyio
async def test_decode_correct_jwt():
    correct_token = await create_token(expire_timedelta=timedelta(seconds=5))

    data = await auth_handler.decode_jwt(correct_token)

    assert data["user_id"] == 1


@pytest.mark.anyio
async def test_decode_expired_jwt():

    with pytest.raises(jwt.ExpiredSignatureError):
        await auth_handler.decode_jwt(
            await create_token(expire_timedelta=timedelta(seconds=-1))
        )


@pytest.mark.anyio
async def test_decode_invalid_jwt():
    inv_token = "invalid"
    with pytest.raises(jwt.InvalidTokenError):
        await auth_handler.decode_jwt(inv_token)
