from sqlalchemy.orm import Session

from app.integration.event_dispatcher import EventDispatcher
from app.notifications.application.handlers.notification_created_handler import (
    NotificationCreatedHandler,
)
from app.notifications.enums import NotificationStatus
from app.notifications.models import Notification
from app.outbox_events.application.ports.outbox_event_publisher import (
    OutboxEventPublisher,
)
from app.outbox_events.enums import OutboxEventStatus
from app.outbox_events.infrastructure.sqs.adapters.sqs_outbox_event_consumer import (
    SQSOutboxEventConsumer,
)
from app.outbox_events.infrastructure.sqs.adapters.sqs_outbox_event_publisher import (
    SQSOutboxEventPublisher,
)
from app.outbox_events.infrastructure.sqs.client import (
    SQSClientConfig,
    create_sqs_client,
)
from app.outbox_events.models import OutboxEvent
from app.settings.app_settings import get_app_settings
from src.workers.notification_delivery_worker import run_listener_once
from src.workers.outbox_publisher_worker import run_orchestrator_once


def test_get_message_from_sqs_and_send_notification(
    db_session: Session, existing_outbox_event: OutboxEvent
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
    sqs_consumer = SQSOutboxEventConsumer(
        sqs_client=sqs_client, queue_url=app_settings.sqs_queue_url
    )
    # TODO: Use a dedicated SQS test queue managed by a pytest fixture.
    sqs_client.purge_queue(
        QueueUrl=app_settings.sqs_queue_url,
    )
    event_dispatcher = EventDispatcher(
        handlers={
            "notification-notification.created": NotificationCreatedHandler(
                db_session=db_session
            )
        }
    )
    run_orchestrator_once(db_session=db_session, event_publisher=sqs_publisher)

    run_listener_once(event_dispatcher=event_dispatcher, outbox_consumer=sqs_consumer)

    db_session.refresh(instance=existing_outbox_event)
    assert existing_outbox_event.status == OutboxEventStatus.PUBLISHED

    notification_db: Notification | None = db_session.get(
        entity=Notification, ident=int(existing_outbox_event.aggregate_id)
    )
    assert notification_db is not None
    assert notification_db.status == NotificationStatus.SENT

    sqs_response = sqs_client.receive_message(
        QueueUrl=app_settings.sqs_queue_url,
        MaxNumberOfMessages=1,
        WaitTimeSeconds=1,
    )
    sqs_messages = sqs_response.get("Messages", [])
    assert len(sqs_messages) == 0
