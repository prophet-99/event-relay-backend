from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from app.users.exceptions import (
    DatabaseOperationException,
    UserEmailAlreadyTakenException,
    UserNotFoundException,
)


def database_operation_exception_handler(
    _req: Request, exc: DatabaseOperationException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "database_operation",
            "message": "An error ocurred during the database operation.",
        },
    )


def user_not_found_exception_handler(
    _req: Request, exc: UserNotFoundException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content={
            "error": "user_not_found",
            "message": f"User with ID {exc.user_id} not found.",
        },
    )


def user_email_already_taken_exception_handler(
    _req: Request, exc: UserEmailAlreadyTakenException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content={
            "error": "user_email_already_taken",
            "message": f"User with email {exc.email} is already taken.",
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        DatabaseOperationException, database_operation_exception_handler
    )
    app.add_exception_handler(UserNotFoundException, user_not_found_exception_handler)
    app.add_exception_handler(
        UserEmailAlreadyTakenException, user_email_already_taken_exception_handler
    )
