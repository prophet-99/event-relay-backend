from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.auth.application.services.auth_service import AuthService
from app.db.database import get_db


def get_auth_service(
    db_session: Annotated[Session, Depends(dependency=get_db)],
) -> AuthService:
    return AuthService(db_session=db_session)


AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]
