from unittest.mock import Mock, patch

from sqlalchemy.orm import Session

from app.outbox_events.application.dto.outbox_event_envelope import OutboxEventEnvelope
from app.outbox_events.application.ports.outbox_event_publisher import (
    OutboxEventPublisher,
)
from app.outbox_events.application.services.outbox_publishing_service import (
    OutboxPublishingService,
)
from app.outbox_events.enums import OutboxEventStatus
from app.outbox_events.models import OutboxEvent


def test_does_not_publish_when_only_non_pending_events_exist(
    db_session: Session, existing_isolated_outbox_event: OutboxEvent
) -> None:
    mock_publisher = Mock(spec_set=OutboxEventPublisher)
    outbox_publishing_service = OutboxPublishingService(
        db_session=db_session, publisher=mock_publisher
    )
    existing_isolated_outbox_event.status = OutboxEventStatus.PUBLISHED
    db_session.flush()

    outbox_publishing_service.publish_next_pending_event()

    mock_publisher.publish.assert_not_called()
    assert existing_isolated_outbox_event.publish_attempt_count == 0
    assert existing_isolated_outbox_event.status == OutboxEventStatus.PUBLISHED


def test_publishes_next_pending_event(
    db_session: Session, existing_isolated_outbox_event: OutboxEvent
) -> None:
    mock_publisher = Mock(spec_set=OutboxEventPublisher)
    outbox_publishing_service = OutboxPublishingService(
        db_session=db_session, publisher=mock_publisher
    )

    outbox_publishing_service.publish_next_pending_event()
    mock_published_envelope: OutboxEventEnvelope = (
        mock_publisher.publish.call_args.kwargs["event"]
    )

    mock_publisher.publish.assert_called_once()
    assert (
        mock_published_envelope.aggregate_id
        == existing_isolated_outbox_event.aggregate_id
    )
    assert mock_published_envelope.event_id == existing_isolated_outbox_event.event_id
    assert (
        mock_published_envelope.aggregate_type
        == existing_isolated_outbox_event.aggregate_type
    )
    assert (
        mock_published_envelope.event_type == existing_isolated_outbox_event.event_type
    )
    assert mock_published_envelope.payload == existing_isolated_outbox_event.payload
    assert existing_isolated_outbox_event.publish_attempt_count == 1
    assert existing_isolated_outbox_event.published_at is not None
    assert existing_isolated_outbox_event.status == OutboxEventStatus.PUBLISHED


def test_does_not_publish_when_pending_event_cannot_be_claimed(
    db_session: Session, existing_isolated_outbox_event: OutboxEvent
) -> None:
    mock_publisher = Mock(spec_set=OutboxEventPublisher)
    outbox_publishing_service = OutboxPublishingService(
        db_session=db_session, publisher=mock_publisher
    )

    with patch.object(
        target=db_session, attribute="execute", return_value=Mock(rowcount=0)
    ) as mock_execute_spy:
        outbox_publishing_service.publish_next_pending_event()

        mock_execute_spy.assert_called_once()

    mock_publisher.publish.assert_not_called()
