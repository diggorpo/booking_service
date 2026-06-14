from fastapi.responses import JSONResponse
from fastapi import APIRouter, Depends, status

from api.api_v1.auth.services import UserService
from .schemas import LoginUserSchema, RegisterUserSchema, UserResponseSchema


router = APIRouter(tags=["Users"])


@router.post(
    "/register", response_model=UserResponseSchema, status_code=status.HTTP_201_CREATED
)
async def register_user(payload: RegisterUserSchema, user_service=Depends(UserService)):
    created_user = await user_service.register_user(payload)
    return created_user


@router.post("/login", status_code=status.HTTP_200_OK)
async def login_user(payload: LoginUserSchema, user_service=Depends(UserService)):

    return await user_service.validate_user(payload.email, payload.password)


# @router.post(
#     "/logout", response_model=UserCreationSchema, status_code=status.HTTP_202_ACCEPTED
# )
# async def logout_user():
#     pass
