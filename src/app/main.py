import logging
from contextlib import asynccontextmanager

import fastapi_swagger_dark as swagger_dark_theme
from fastapi import APIRouter, FastAPI

from app.api.v1.router import router as api_router_v1
from app.db.database import SqlAlchemyBase, engine
from app.exceptions.handlers import register_exception_handlers
from app.notifications.models import Notification
from app.outbox_events.models import OutboxEvent
from app.schedules.models import Schedule
from app.users.models import User
from app.web.router import router as web_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    SqlAlchemyBase.metadata.create_all(
        bind=engine,
        tables=[
            Schedule.__table__,
            User.__table__,
            Notification.__table__,
            OutboxEvent.__table__,
        ],
    )
    yield


app = FastAPI(title="Schedule API", version="1.0.0", lifespan=lifespan, docs_url=None)

# Swagger - dark theme
docs_router = APIRouter()
swagger_dark_theme.install(docs_router)
app.include_router(docs_router)

# Routes
app.include_router(web_router)
app.include_router(api_router_v1, prefix="/api/v1")

# Handlers
register_exception_handlers(app)
