from fastapi import APIRouter, Depends, status
from .schemas import UserCreationSchema
from api.deps.db_session import get_db_session
from core.infrastructure.db.repositories.users import SQLAlchemyBaseRepository

router = APIRouter(tags=["Users"])


@router.post(
    "/login", response_model=UserCreationSchema, status_code=status.HTTP_201_CREATED
)
async def create_user(payload: UserCreationSchema, session=Depends(get_db_session)):
    pass


@router.patch(
    "", response_model=UserCreationSchema, status_code=status.HTTP_202_ACCEPTED
)
async def update_user():
    pass


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user():
    pass
