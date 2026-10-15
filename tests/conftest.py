from collections.abc import Generator

import pytest
from sqlalchemy import Engine, StaticPool, create_engine, event
from sqlalchemy.orm import Session

from app.db.database import SqlAlchemyBase

# Only for SqlAlchemyBase.metadata.create_all
from app.notifications.models import Notification  # noqa: F401
from app.outbox_events.models import OutboxEvent  # noqa: F401
from app.schedules.models import Schedule  # noqa: F401
from app.users.models import User  # noqa: F401

pytest_plugins = (
    "tests.fixtures.users",
    "tests.fixtures.outbox_events",
)


@pytest.fixture(scope="session")
def test_engine() -> Generator[Engine, None, None]:
    database_url = "sqlite+pysqlite:///:memory:"
    engine = create_engine(
        database_url, connect_args={"check_same_thread": False}, poolclass=StaticPool
    )

    @event.listens_for(engine, identifier="connect")
    def _enable_sqlite_foreign_keys(dbapi_connection, _connection_record) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    SqlAlchemyBase.metadata.create_all(bind=engine)

    try:
        yield engine
    finally:
        SqlAlchemyBase.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture
def db_session(test_engine: Engine) -> Generator[Session, None, None]:
    connection = test_engine.connect()
    outer_transaction = connection.begin()

    session = Session(
        bind=connection,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
        join_transaction_mode="rollback_only",
    )

    try:
        yield session
    finally:
        session.close()
        if outer_transaction.is_active:
            outer_transaction.rollback()
        connection.close()
