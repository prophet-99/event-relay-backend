from fastapi.routing import APIRouter

from app.api.v1.health import router as health_router
from app.schedules.router import router as schedules_router

router = APIRouter()
router.include_router(health_router)
router.include_router(schedules_router)
