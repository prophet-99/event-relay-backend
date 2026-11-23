import logging

from pydantic import SecretStr
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.auth.application.exceptions import (
    DatabaseOperationException,
    InvalidCredentialsException,
    PasswordChangeRequiredException,
)
from app.auth.application.schemas import (
    AuthLoginRequest,
    AuthTokenResponse,
    ChangePasswordRequest,
)
from app.security.password_hasher import hash_password, verify_password
from app.security.token_service import create_access_token
from app.users.models import User

logger: logging.Logger = logging.getLogger(name=__name__)


class AuthService:
    def __init__(self, db_session: Session):
        self._db_session: Session = db_session

    def _is_valid_user(self, *, email: str, password: SecretStr) -> User:
        statement = select(User).where(User.email == email, User.is_enabled.is_(True))
        matched_user: User | None = self._db_session.scalar(statement=statement)
        if matched_user is None:
            logger.info(msg="The user didn't match")
            raise InvalidCredentialsException()

        password_matches: bool = verify_password(
            plain_password=password.get_secret_value(),
            stored_password_hash=matched_user.hashed_password,
        )
        if password_matches is False:
            logger.info(msg="The password didn't match")
            raise InvalidCredentialsException()

        return matched_user

    def login(self, auth_login_request: AuthLoginRequest) -> AuthTokenResponse:
        matched_user: User = self._is_valid_user(
            email=auth_login_request.email, password=auth_login_request.password
        )
        if matched_user.must_change_password is True:
            logger.info(msg="The user didn't change your password")
            raise PasswordChangeRequiredException()

        jwt: str = create_access_token(user_id=matched_user.id)

        return AuthTokenResponse(jwt=jwt, token_type="bearer")

    def change_password(self, change_password_request: ChangePasswordRequest) -> None:
        matched_user: User = self._is_valid_user(
            email=change_password_request.email,
            password=change_password_request.password,
        )

        try:
            matched_user.must_change_password = False
            matched_user.hashed_password = hash_password(
                plain_password=change_password_request.new_password.get_secret_value()
            )

            self._db_session.commit()
        except SQLAlchemyError as exc:
            self._db_session.rollback()
            logger.error(msg="The user's password didn't can change")

            raise DatabaseOperationException() from exc
