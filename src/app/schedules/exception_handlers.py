from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from app.schedules.exceptions import ScheduleNotFoundException


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


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        ScheduleNotFoundException, schedule_not_found_exception_handler
    )
