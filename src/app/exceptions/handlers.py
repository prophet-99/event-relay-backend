from fastapi import FastAPI, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHttpException

from app.schedules.exception_handlers import (
    register_exception_handlers as schedules_register_exception_handlers,
)


def starlette_http_exception_handler(
    _request: Request, ex: StarletteHttpException
) -> JSONResponse:
    return JSONResponse(
        status_code=ex.status_code,
        content={
            "error": "http_error",
            "message": ex.detail,
        },
    )


def request_validation_exception_handler(
    _request: Request, ex: RequestValidationError
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content=jsonable_encoder({"error": "validation_error", "message": ex.errors()}),
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(StarletteHttpException, starlette_http_exception_handler)
    app.add_exception_handler(
        RequestValidationError, request_validation_exception_handler
    )
    schedules_register_exception_handlers(app)
