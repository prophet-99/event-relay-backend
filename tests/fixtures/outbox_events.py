from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from app.outbox_events.constants import MAX_PUBLISH_ATTEMPTS
from app.outbox_events.enums import OutboxEventStatus
from app.outbox_events.models import OutboxEvent


@pytest.fixture
def existing_isolated_outbox_event(db_session: Session) -> OutboxEvent:
    new_outbox_event = OutboxEvent(
        aggregate_id="XXX",
        aggregate_type="notification",
        event_id=str(uuid4()),
        event_type="notification.created",
        status=OutboxEventStatus.PENDING,
        payload={},
        max_publish_attempts=MAX_PUBLISH_ATTEMPTS,
    )

    db_session.add(new_outbox_event)
    db_session.flush()
    db_session.refresh(new_outbox_event)

    return new_outbox_event
