from fastapi import Depends, HTTPException, status
from typing import Annotated

import jwt

from api.api_v1.auth.schemas import UserResponseSchema
from api.api_v1.auth.service import UserService
from ..api_v1.auth.utils import get_token_from_cookie
from ..api_v1.auth.handler import AuthHandler


async def get_current_user(
    token: Annotated[str, Depends(get_token_from_cookie)],
    handler: AuthHandler = Depends(AuthHandler),
    user_service: UserService = Depends(UserService),
) -> UserResponseSchema:
    try:
        decoded_token = await handler.decode_jwt(token)
        user_id = decoded_token.get("user_id")

        user = await user_service.get_user_by_id(user_id)
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
