from fastapi import FastAPI

from app.api.v1.router import router as api_router_v1
from app.exceptions.handlers import register_exception_handlers
from app.web.router import router as web_router

app = FastAPI(title="Schedule API", version="1.0.0")

# Routes
app.include_router(web_router)
app.include_router(api_router_v1, prefix="/api/v1")

# Handlers
register_exception_handlers(app)
