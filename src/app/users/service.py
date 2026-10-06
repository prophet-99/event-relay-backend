import logging

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.users.exceptions import (
    DatabaseOperationException,
    UserEmailAlreadyTakenException,
    UserNotFoundException,
)
from app.users.models import User
from app.users.schemas import UserCreate, UserResponse, UserUpdate

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, db: Session):
        self._db = db

    def _get_user_or_raise(self, user_id: int) -> User:
        user_db = self._db.get(User, user_id)
        if user_db is None:
            raise UserNotFoundException(user_id)

        return user_db

    def _commit_or_raise(self) -> None:
        try:
            self._db.commit()
        except SQLAlchemyError:
            self._db.rollback()

            raise

    def get_all(self) -> list[UserResponse]:
        statement = select(User)
        statement = statement.where(User.is_enabled.is_(True))

        users = self._db.scalars(statement).all()

        return [UserResponse.model_validate(user) for user in users]

    def get_by_id(self, user_id: int) -> UserResponse:
        user_db = self._get_user_or_raise(user_id)

        return UserResponse.model_validate(user_db)

    def create(self, user_request: UserCreate) -> UserResponse:
        new_user = User(**user_request.model_dump())

        try:
            self._db.add(new_user)
            self._commit_or_raise()

            return UserResponse.model_validate(new_user)
        except IntegrityError as exc:
            logger.exception("Email already exists")

            raise UserEmailAlreadyTakenException(new_user.email) from exc
        except SQLAlchemyError as exc:
            logger.exception("SQLAlchemyError Exception")

            raise DatabaseOperationException from exc

    def update(self, user_id: int, user_request: UserUpdate) -> UserResponse:
        user_to_update = self._get_user_or_raise(user_id)
        user_changes = user_request.model_dump(exclude_unset=True)

        for key, value in user_changes.items():
            setattr(user_to_update, key, value)

        try:
            self._commit_or_raise()

            return UserResponse.model_validate(user_to_update)
        except IntegrityError as exc:
            logger.exception("Integrity error")

            if "email" in user_changes:
                raise UserEmailAlreadyTakenException(user_changes["email"]) from exc
            raise DatabaseOperationException from exc
        except SQLAlchemyError as exc:
            logger.exception("SQLAlchemyError Exception")

            raise DatabaseOperationException from exc

    def delete(self, user_id: int) -> UserResponse:
        user_to_update = self._get_user_or_raise(user_id)
        user_to_update.is_enabled = False

        try:
            self._commit_or_raise()

            return UserResponse.model_validate(user_to_update)
        except SQLAlchemyError as exc:
            logger.exception("SQLAlchemyError Exception")

            raise DatabaseOperationException from exc
