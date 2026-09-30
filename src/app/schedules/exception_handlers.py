from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from app.schedules.exceptions import (
    DatabaseOperationException,
    ScheduleNotFoundException,
)


def schedule_not_found_exception_handler(
    _request: Request, ex: ScheduleNotFoundException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": "schedule_not_found",
            "message": f"Schedule with ID {ex.schedule_id} not found.",
        },
    )


def database_operation_exception_handler(
    _request: Request, _ex: DatabaseOperationException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "database_operation",
            "message": "An error ocurred during the database operation.",
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        ScheduleNotFoundException, schedule_not_found_exception_handler
    )
    app.add_exception_handler(
        DatabaseOperationException, database_operation_exception_handler
    )
