from fastapi import APIRouter, Depends

from api.api_v1.auth.schemas import RolesEnum
from api.deps.require_role import require_role

from .auth.views import router as auth_router
from .slots.views import router as slots_router
from .bookings.views import router as bookings_router
from .bookings.admin.views import router as admin_booking_router


router = APIRouter()
router.include_router(router=auth_router, prefix="/auth")
router.include_router(router=slots_router, prefix="/slots")
router.include_router(router=bookings_router, prefix="/bookings")
router.include_router(
    router=admin_booking_router,
    prefix="/admin/booking",
    dependencies=[Depends(require_role(RolesEnum.ADMIN))],
)
