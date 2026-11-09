from typing import cast

from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from starlette.types import ExceptionHandler

from app.notifications.application.exceptions.persistence_exceptions import (
    DatabaseException,
)


def _database_exception_handler(
    _request: Request, exc: DatabaseException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "database",
            "message": "An error ocurred during the database operation.",
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        exc_class_or_status_code=DatabaseException,
        handler=cast(
            typ=ExceptionHandler, val=_database_exception_handler
        ),  # CAST TO AVOID WARNING ISSUE
    )
