from unittest.mock import Mock, patch

from sqlalchemy.orm import Session

from app.outbox_events.application.ports.outbox_event_publisher import (
    OutboxEventPublisher,
)
from app.outbox_events.application.services.outbox_publishing_service import (
    OutboxPublishingService,
)
from workers.outbox_publisher_worker import run_orchestrator_once


def test_delegates_once_to_outbox_publishing_service() -> None:
    publisher_mock = Mock(spec_set=OutboxEventPublisher)
    db_session_mock = Mock(spec_set=Session)

    with patch.object(
        target=OutboxPublishingService,
        attribute="publish_next_pending_event",
        return_value=None,
    ) as publish_next_pending_event_spy:
        run_orchestrator_once(
            db_session=db_session_mock, event_publisher=publisher_mock
        )

        publish_next_pending_event_spy.assert_called_once()
