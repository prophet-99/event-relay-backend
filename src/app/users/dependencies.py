from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.users.service import UserService


def get_user_service(db: Annotated[Session, Depends(get_db)]) -> UserService:
    return UserService(db)


UserServiceDep = Annotated[UserService, Depends(get_user_service)]
