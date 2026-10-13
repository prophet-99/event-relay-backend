import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import router as api_router_v1
from app.db.database import SqlAlchemyBase, engine
from app.exceptions.handlers import register_exception_handlers
from app.notifications.models import Notification
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
        bind=engine, tables=[Schedule.__table__, User.__table__, Notification.__table__]
    )
    yield


app = FastAPI(title="Schedule API", version="1.0.0", lifespan=lifespan)

# Routes
app.include_router(web_router)
app.include_router(api_router_v1, prefix="/api/v1")

# Handlers
register_exception_handlers(app)
