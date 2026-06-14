from fastapi import Depends
from typing import Annotated

from api.api_v1.auth.schemas import UserResponseSchema
from api.api_v1.auth.services import UserService
from .utils import get_token_from_cookie
from .handler import AuthHandler


async def get_current_user(
    token: Annotated[str, Depends(get_token_from_cookie)],
    handler: AuthHandler = Depends(AuthHandler),
    user_service: UserService = Depends(UserService),
) -> UserResponseSchema:

    decoded_token = await handler.decode_jwt(token)
    user_id = decoded_token.get("user_id")

    user = await user_service.get_user_by_id(user_id)
    return user
