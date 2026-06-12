from fastapi import APIRouter, status
from .schemas import UserCreationSchema

router = APIRouter(tags=["Users"])


@router.post(
    "/create", response_model=UserCreationSchema, status_code=status.HTTP_201_CREATED
)
async def create_user():
    pass


@router.patch(
    "/update", response_model=UserCreationSchema, status_code=status.HTTP_202_ACCEPTED
)
async def update_user():
    pass


@router.delete("/delete", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user():
    pass
