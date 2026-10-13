from datetime import date

import pytest
from sqlalchemy.orm import Session

from app.users.models import User


@pytest.fixture
def existing_user(db_session: Session) -> User:
    new_user = User(
        name="Alexander",
        last_name="Alcachofa Noqa",
        birthday_date=date(year=1999, month=12, day=16),
        email="alex_alcachofa@gmail.com",
    )

    db_session.add(new_user)
    db_session.flush()

    return new_user
