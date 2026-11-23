from fastapi.routing import APIRouter

from app.api.v1.health import router as health_router
from app.auth.infrastructure.router import router as auth_router
from app.notifications.router import router as notification_router
from app.schedules.router import router as schedules_router
from app.users.router import router as user_router

router = APIRouter()
router.include_router(health_router)
router.include_router(schedules_router)
router.include_router(user_router)
router.include_router(notification_router)
router.include_router(auth_router)
