import signal
from collections.abc import Callable
from threading import Event
from time import sleep as default_sleep

from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.outbox_events.application.ports.outbox_event_publisher import (
    OutboxEventPublisher,
)
from app.outbox_events.application.services.outbox_publishing_service import (
    OutboxPublishingService,
)
from app.outbox_events.infrastructure.sqs.adapters.sqs_outbox_event_publisher import (
    SQSOutboxEventPublisher,
)
from app.outbox_events.infrastructure.sqs.client import (
    SQSClientConfig,
    create_sqs_client,
)
from app.settings.app_settings import get_app_settings


def run_orchestrator_once(
    db_session: Session, event_publisher: OutboxEventPublisher
) -> None:
    outbox_publishing_service = OutboxPublishingService(
        db_session=db_session, publisher=event_publisher
    )
    outbox_publishing_service.publish_next_pending_event()


def run_forever(
    event_publisher: OutboxEventPublisher,
    session_factory: Callable[[], Session] = SessionLocal,
    stop_event: Event | None = None,
    sleep: Callable[[float], None] = default_sleep,
    poll_interval_seconds: float = 1.0,
) -> None:
    worker_stop_event = stop_event or Event()

    while not worker_stop_event.is_set():
        with session_factory() as db_session:
            run_orchestrator_once(
                db_session=db_session, event_publisher=event_publisher
            )
        sleep(poll_interval_seconds)


def main() -> None:
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
    stop_event = Event()
    signal.signal(signalnum=signal.SIGTERM, handler=lambda *_: stop_event.set())
    signal.signal(
        signalnum=signal.SIGINT, handler=lambda _signal_number, _frame: stop_event.set()
    )

    run_forever(event_publisher=sqs_publisher, stop_event=stop_event)


if __name__ == "__main__":
    main()
