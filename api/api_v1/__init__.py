from fastapi import APIRouter

from .auth.views import router as auth_router
from .slots.views import router as slots_router
from .bookings.views import router as bookings_router


router = APIRouter()
router.include_router(router=auth_router, prefix="/auth")
router.include_router(router=slots_router, prefix="/slots")
router.include_router(router=bookings_router, prefix="/bookings")
