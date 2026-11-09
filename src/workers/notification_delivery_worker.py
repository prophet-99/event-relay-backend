from botocore.client import BaseClient

from app.db.database import SessionLocal
from app.integration.event_dispatcher import EventDispatcher
from app.notifications.application.exceptions.delivery_exceptions import (
    NotificationAlreadySentException,
    NotificationDeliveryException,
    NotificationNotFoundException,
)
from app.notifications.application.handlers.notification_created_handler import (
    NotificationCreatedHandler,
)
from app.outbox_events.application.ports.outbox_event_consumer import (
    OutboxEventConsumer,
    OutboxEventReceiveResponse,
)
from app.outbox_events.infrastructure.sqs.adapters.sqs_outbox_event_consumer import (
    SQSOutboxEventConsumer,
)
from app.outbox_events.infrastructure.sqs.client import (
    SQSClientConfig,
    create_sqs_client,
)
from app.settings.app_settings import _AppSettings, get_app_settings


def run_listener_once(
    outbox_consumer: OutboxEventConsumer,
    event_dispatcher: EventDispatcher,
) -> None:
    outbox_response: OutboxEventReceiveResponse | None = outbox_consumer.receive()
    if outbox_response is None:
        return
    try:
        event_dispatcher.dispatch(
            outbox_event_dto=outbox_response["outbox_event_envelope"]
        )
        outbox_consumer.delete(receipt_handle=outbox_response["receipt_handle"])
    except NotificationDeliveryException:
        print("It's a SQL Alchemy Error")
    except (NotificationAlreadySentException, NotificationNotFoundException):
        outbox_consumer.delete(receipt_handle=outbox_response["receipt_handle"])


if __name__ == "__main__":
    app_settings: _AppSettings = get_app_settings()
    sqs_client: BaseClient = create_sqs_client(
        config=SQSClientConfig(
            region_name=app_settings.aws_region,
            endpoint_url=app_settings.sqs_endpoint_url,
        )
    )
    sqs_consumer = SQSOutboxEventConsumer(
        queue_url=app_settings.sqs_queue_url, sqs_client=sqs_client
    )

    with SessionLocal() as db_session:
        event_dispatcher = EventDispatcher(
            handlers={
                "notification-notification.created": NotificationCreatedHandler(
                    db_session=db_session
                )
            }
        )
        run_listener_once(
            outbox_consumer=sqs_consumer,
            event_dispatcher=event_dispatcher,
        )
