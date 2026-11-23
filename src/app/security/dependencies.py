from datetime import datetime, timezone
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.security.exceptions import InvalidTokenException
from app.security.schemas import AccessTokenPayload, AuthenticationSecurity
from app.security.token_service import extract_payload
from app.users.models import User

http_bearer = HTTPBearer()


def get_jwt_payload(
    authorization: Annotated[
        HTTPAuthorizationCredentials, Depends(dependency=http_bearer)
    ],
    db_session: Annotated[Session, Depends(dependency=get_db)],
) -> AuthenticationSecurity:
    payload: AccessTokenPayload = extract_payload(jwt=authorization.credentials)
    user_id: int
    try:
        user_id = int(payload.sub)
    except ValueError as exc:
        raise InvalidTokenException() from exc

    statement = select(User).where(User.id == user_id, User.is_enabled.is_(True))
    db_user: User | None = db_session.scalar(statement=statement)

    if db_user is None:
        raise InvalidTokenException()

    return AuthenticationSecurity(
        user=db_user,
        expires_at=datetime.fromtimestamp(
            payload.exp,
            tz=timezone.utc,
        ),
    )


AuthenticationSecurityDep = Annotated[
    AuthenticationSecurity, Depends(dependency=get_jwt_payload)
]
