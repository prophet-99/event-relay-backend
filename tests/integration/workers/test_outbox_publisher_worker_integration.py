import json

from sqlalchemy.orm import Session

from app.outbox_events.application.ports.outbox_event_publisher import (
    OutboxEventPublisher,
)
from app.outbox_events.enums import OutboxEventStatus
from app.outbox_events.infrastructure.sqs.adapters.sqs_outbox_event_publisher import (
    SQSOutboxEventPublisher,
)
from app.outbox_events.infrastructure.sqs.client import (
    SQSClientConfig,
    create_sqs_client,
)
from app.outbox_events.models import OutboxEvent
from app.settings.app_settings import get_app_settings
from workers.outbox_publisher_worker import run_orchestrator_once


def test_send_message_to_sqs_when_exists_pending_outbox_events(
    db_session: Session,
    existing_isolated_outbox_event: OutboxEvent,
) -> None:
    app_settings = get_app_settings()
    sqs_client = create_sqs_client(
        config=SQSClientConfig(
            region_name=app_settings.aws_region,
            endpoint_url=app_settings.sqs_endpoint_url,
        )
    )
    sqs_publisher: OutboxEventPublisher = SQSOutboxEventPublisher(
        sqs_client=sqs_client, queue_url=app_settings.sqs_queue_url
    )
    # TODO: Use a dedicated SQS test queue managed by a pytest fixture.
    sqs_client.purge_queue(
        QueueUrl=app_settings.sqs_queue_url,
    )

    run_orchestrator_once(db_session=db_session, event_publisher=sqs_publisher)

    db_session.refresh(existing_isolated_outbox_event)
    assert existing_isolated_outbox_event.status == OutboxEventStatus.PUBLISHED
    assert existing_isolated_outbox_event.publish_attempt_count == 1
    assert existing_isolated_outbox_event.published_at is not None

    sqs_response = sqs_client.receive_message(
        QueueUrl=app_settings.sqs_queue_url,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=1,
    )
    sqs_messages = sqs_response.get("Messages", [])
    assert len(sqs_messages) == 1
    message_body = json.loads(sqs_messages[0]["Body"])
    assert message_body == {
        "event_id": existing_isolated_outbox_event.event_id,
        "aggregate_id": existing_isolated_outbox_event.aggregate_id,
        "aggregate_type": existing_isolated_outbox_event.aggregate_type,
        "event_type": existing_isolated_outbox_event.event_type,
        "payload": existing_isolated_outbox_event.payload,
    }
