from fastapi import APIRouter

from app.auth.application.schemas import AuthLoginRequest, AuthTokenResponse
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
