from fastapi import FastAPI, status
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from app.auth.application.exceptions import (
    InvalidCredentialsException,
    PasswordChangeRequiredException,
)


def invalid_credentials_exception_handler(
    _req: Request, exc: InvalidCredentialsException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "error": "authentication_error",
            "message": str(exc),
        },
    )


def password_change_required_exception_handler(
    _req: Request, exc: PasswordChangeRequiredException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_403_FORBIDDEN,
        content={
            "error": "password_change_required",
            "message": str(exc),
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        exc_class_or_status_code=InvalidCredentialsException,
        handler=invalid_credentials_exception_handler,
    )
    app.add_exception_handler(
        exc_class_or_status_code=PasswordChangeRequiredException,
        handler=password_change_required_exception_handler,
    )
