from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from app.security.exceptions import (
    ExpiredAccessTokenException,
    InvalidTokenException,
    RequiredClaimsTokenException,
)


def expired_access_exception_handler(
    _req: Request, exc: ExpiredAccessTokenException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "error": "access_token_error",
            "message": str(exc),
        },
    )


def required_claims_exception_handler(
    _req: Request, exc: RequiredClaimsTokenException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "error": "access_token_error",
            "message": str(exc),
        },
    )


def invalid_token_exception_handler(
    _req: Request, exc: InvalidTokenException
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={
            "error": "access_token_error",
            "message": str(exc),
        },
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(
        exc_class_or_status_code=ExpiredAccessTokenException,
        handler=expired_access_exception_handler,
    )
    app.add_exception_handler(
        exc_class_or_status_code=RequiredClaimsTokenException,
        handler=required_claims_exception_handler,
    )
    app.add_exception_handler(
        exc_class_or_status_code=InvalidTokenException,
        handler=invalid_token_exception_handler,
    )
