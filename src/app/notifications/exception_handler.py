from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from app.notifications.exceptions import DatabaseException


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
    app.add_exception_handler(DatabaseException, _database_exception_handler)
