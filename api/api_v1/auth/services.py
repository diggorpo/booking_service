from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from api.api_v1.auth.handler import AuthHandler
from api.api_v1.auth.schemas import (
    RegisterUserSchema,
    UserResponseSchema,
    CreateUserSchema,
)
from api.deps.db_session import get_db_session
from core.infrastructure.db.repositories.users import UserRepository


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
    
    async def validate_user(self, email: str, password: str) -> UserResponseSchema | None:

