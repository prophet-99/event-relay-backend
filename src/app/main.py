from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.v1.router import router as api_router_v1
from app.db.database import SqlAlchemyBase, engine
from app.exceptions.handlers import register_exception_handlers
from app.schedules.models import Schedule
from app.web.router import router as web_router


@asynccontextmanager
async def lifespan(_app: FastAPI):
    SqlAlchemyBase.metadata.create_all(bind=engine, tables=[Schedule.__table__])
    yield


app = FastAPI(title="Schedule API", version="1.0.0", lifespan=lifespan)

# Routes
app.include_router(web_router)
app.include_router(api_router_v1, prefix="/api/v1")

# Handlers
register_exception_handlers(app)
