from fastapi import APIRouter, status

from app.auth.application.schemas import (
    AuthLoginRequest,
    AuthTokenResponse,
    ChangePasswordRequest,
)
from app.auth.infrastructure.dependency_injection.auth_dependencies import (
    AuthServiceDep,
)

router = APIRouter(prefix="/auth", tags=["Auth Module"])


@router.post(
    path="/login",
    summary="Login user by email and password",
    response_model=AuthTokenResponse,
)
def login(auth_service: AuthServiceDep, request: AuthLoginRequest) -> AuthTokenResponse:
    return auth_service.login(auth_login_request=request)


@router.post(
    path="/change-password",
    summary="Change password by email and passwords (old and new)",
    status_code=status.HTTP_204_NO_CONTENT,
)
def change_password(
    auth_service: AuthServiceDep, request: ChangePasswordRequest
) -> None:
    auth_service.change_password(change_password_request=request)
