from fastapi import Depends, HTTPException, status

from api.api_v1.auth.schemas import RolesEnum, UserResponseSchema
from api.deps.get_current_user import get_current_user


async def require_role(
    role: RolesEnum,
    user: UserResponseSchema = Depends(get_current_user),
) -> UserResponseSchema:

    if user.role.name == role:
        return user

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN, detail="Permission denied"
    )
