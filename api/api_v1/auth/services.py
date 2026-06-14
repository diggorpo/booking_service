from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from api.api_v1.auth.handler import AuthHandler
from api.api_v1.auth.schemas import (
    RegisterUserSchema,
    UserResponseSchema,
    CreateUserSchema,
)
from api.deps.db_session import get_db_session
from core.infrastructure.db.repositories.users import UserRepository
from core.config import settings


class UserService:
    def __init__(
        self,
        db_session: AsyncSession = Depends(get_db_session),
        user_repo: UserRepository = Depends(UserRepository),
        auth_handler: AuthHandler = Depends(AuthHandler),
    ):
        self.db_session = db_session
        self.user_repo = user_repo
        self.auth_handler = auth_handler

    async def register_user(self, user: RegisterUserSchema) -> UserResponseSchema:
        hashed = self.auth_handler.hash_password(user.password)

        db_dto = CreateUserSchema(**user.model_dump(), password_hash=hashed)

        created_user = await self.user_repo.create(self.db_session, db_dto.model_dump())
        await self.db_session.commit()
        return UserResponseSchema.model_validate(created_user)

    async def validate_user(self, email: str, password: str) -> JSONResponse | None:

        user = await self.user_repo.find_one(self.db_session, email=email)
        if not user or not self.auth_handler.validate_password(
            password, user.password_hash
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password",
            )
        jwt_token, session_id = await self.auth_handler.encode_jwt({"user_id": user.id})
        response = JSONResponse(content={"massege": "Login successful"})
        response.set_cookie(
            key="Authorization",
            value=jwt_token,
            httponly=True,
            max_age=settings.auth_jwt.access_token_expire_minutes * 60,
        )

        return response
