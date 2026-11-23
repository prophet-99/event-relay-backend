from datetime import datetime, timedelta, timezone

import pytest
from fastapi.security import HTTPAuthorizationCredentials
from jwt import encode
from sqlalchemy.orm import Session

from app.auth.application.exceptions import (
    InvalidCredentialsException,
    PasswordChangeRequiredException,
)
from app.auth.application.schemas import AuthLoginRequest, ChangePasswordRequest
from app.auth.application.services.auth_service import AuthService
from app.security.dependencies import get_jwt_payload
from app.security.exceptions import ExpiredAccessTokenException, InvalidTokenException
from app.security.password_hasher import verify_password
from app.security.token_service import create_access_token, extract_payload
from app.users.models import User
from tests.fixtures.security import JwtSettings, create_jwt_settings  # noqa: F401


def test_login_returns_access_token_for_user_without_password_change_requirement(
    db_session: Session, existing_user: User, jwt_settings: JwtSettings
) -> None:
    # Arrange
    existing_user.must_change_password = False
    db_session.flush()
    auth_service = AuthService(db_session)
    request = AuthLoginRequest(email=existing_user.email, password="secure12")

    # Act
    response = auth_service.login(request)

    # Assert
    payload = extract_payload(response.jwt)
    assert payload.sub == str(existing_user.id)
    assert response.token_type == "bearer"


def test_login_rejects_invalid_password(
    db_session: Session, existing_user: User
) -> None:
    # Arrange
    auth_service = AuthService(db_session)
    request = AuthLoginRequest(email=existing_user.email, password="incorrect")

    # Act / Assert
    with pytest.raises(InvalidCredentialsException):
        auth_service.login(request)


def test_login_requires_password_change_for_temporary_password(
    db_session: Session, existing_user: User
) -> None:
    # Arrange
    auth_service = AuthService(db_session)
    request = AuthLoginRequest(email=existing_user.email, password="secure12")

    # Act / Assert
    with pytest.raises(PasswordChangeRequiredException):
        auth_service.login(request)


def test_change_password_updates_user_credentials(
    db_session: Session, existing_user: User
) -> None:
    # Arrange
    auth_service = AuthService(db_session)
    change_password_request = ChangePasswordRequest(
        email=existing_user.email,
        password="secure12",
        new_password="newpass1",
    )

    # Act
    auth_service.change_password(change_password_request)

    # Assert
    db_session.refresh(existing_user)
    assert existing_user.must_change_password is False
    assert verify_password(
        plain_password="newpass1",
        stored_password_hash=existing_user.hashed_password,
    )


def test_login_returns_access_token_after_password_change(
    db_session: Session, existing_user: User, jwt_settings: JwtSettings
) -> None:
    # Arrange
    auth_service = AuthService(db_session)
    auth_service.change_password(
        ChangePasswordRequest(
            email=existing_user.email,
            password="secure12",
            new_password="newpass1",
        )
    )
    login_request = AuthLoginRequest(
        email=existing_user.email,
        password="newpass1",
    )

    # Act
    response = auth_service.login(login_request)

    # Assert
    assert extract_payload(response.jwt).sub == str(existing_user.id)


def test_login_rejects_disabled_user(
    db_session: Session, existing_user: User
) -> None:
    # Arrange
    existing_user.is_enabled = False
    db_session.flush()
    auth_service = AuthService(db_session)
    request = AuthLoginRequest(email=existing_user.email, password="secure12")

    # Act / Assert
    with pytest.raises(InvalidCredentialsException):
        auth_service.login(request)


def test_jwt_dependency_returns_enabled_current_user(
    db_session: Session, existing_user: User, jwt_settings: JwtSettings
) -> None:
    # Arrange
    existing_user.must_change_password = False
    db_session.flush()
    access_token = create_access_token(user_id=existing_user.id)
    authorization = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials=access_token
    )

    # Act
    authentication = get_jwt_payload(
        authorization=authorization,
        db_session=db_session,
    )

    # Assert
    assert authentication.user.id == existing_user.id
    assert authentication.expires_at > datetime.now(tz=timezone.utc)


def test_jwt_dependency_rejects_disabled_user(
    db_session: Session, existing_user: User, jwt_settings: JwtSettings
) -> None:
    # Arrange
    access_token = create_access_token(user_id=existing_user.id)
    existing_user.is_enabled = False
    db_session.flush()
    authorization = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials=access_token
    )

    # Act / Assert
    with pytest.raises(InvalidTokenException):
        get_jwt_payload(
            authorization=authorization,
            db_session=db_session,
        )


def test_extract_payload_rejects_expired_token(jwt_settings: JwtSettings) -> None:
    # Arrange
    expired_token = encode(
        payload={
            "sub": "1",
            "exp": datetime.now(tz=timezone.utc) - timedelta(minutes=1),
        },
        key=jwt_settings.jwt_secret_key,
        algorithm=jwt_settings.jwt_algorithm,
    )

    # Act / Assert
    with pytest.raises(ExpiredAccessTokenException):
        extract_payload(expired_token)


def test_jwt_dependency_rejects_non_numeric_subject(
    db_session: Session, jwt_settings: JwtSettings
) -> None:
    # Arrange
    malformed_token = encode(
        payload={
            "sub": "not-a-number",
            "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=1),
        },
        key=jwt_settings.jwt_secret_key,
        algorithm=jwt_settings.jwt_algorithm,
    )
    authorization = HTTPAuthorizationCredentials(
        scheme="Bearer", credentials=malformed_token
    )

    # Act / Assert
    with pytest.raises(InvalidTokenException):
        get_jwt_payload(
            authorization=authorization,
            db_session=db_session,
        )
