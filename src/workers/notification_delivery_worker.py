import signal
from collections.abc import Callable
from threading import Event
from time import sleep as default_sleep

from botocore.client import BaseClient
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.integration.event_dispatcher import EventDispatcher
from app.notifications.application.exceptions.delivery_exceptions import (
    NotificationAlreadySendingException,
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
from app.schedules.models import Schedule  # noqa: F401
from app.settings.app_settings import _AppSettings, get_app_settings
from app.users.models import User  # noqa: F401


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
    except (NotificationDeliveryException, NotificationAlreadySendingException) as exc:
        print(f"This error don't need ACK: {exc}")
    except (NotificationAlreadySentException, NotificationNotFoundException):
        outbox_consumer.delete(receipt_handle=outbox_response["receipt_handle"])


def run_forever(
    outbox_consumer: OutboxEventConsumer,
    session_factory: Callable[[], Session] = SessionLocal,
    stop_event: Event | None = None,
    sleep: Callable[[float], None] = default_sleep,
    poll_interval_seconds: float = 1.0,
) -> None:
    worker_stop_event = stop_event or Event()

    while not worker_stop_event.is_set():
        with session_factory() as db_session:
            event_dispatcher = EventDispatcher(
                handlers={
                    "notification-notification.created": NotificationCreatedHandler(
                        db_session=db_session
                    )
                }
            )
            run_listener_once(
                outbox_consumer=outbox_consumer,
                event_dispatcher=event_dispatcher,
            )
        sleep(poll_interval_seconds)


def main() -> None:
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
    stop_event = Event()
    signal.signal(signalnum=signal.SIGTERM, handler=lambda *_: stop_event.set())
    signal.signal(signalnum=signal.SIGINT, handler=lambda *_: stop_event.set())

    run_forever(outbox_consumer=sqs_consumer, stop_event=stop_event)


if __name__ == "__main__":
    main()
