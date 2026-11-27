from threading import Event
from unittest.mock import Mock, patch

from workers import notification_delivery_worker, outbox_publisher_worker


class _SessionContext:
    def __init__(self) -> None:
        self.entered = 0
        self.exited = 0

    def __enter__(self) -> object:
        self.entered += 1
        return object()

    def __exit__(
        self, _exc_type: object, _exc_value: object, _traceback: object
    ) -> None:
        self.exited += 1


def test_outbox_loop_closes_the_session_before_waiting() -> None:
    stop_event = Event()
    session_context = _SessionContext()
    sleep = Mock(side_effect=lambda _seconds: stop_event.set())

    with patch.object(outbox_publisher_worker, "run_orchestrator_once") as run_once:
        outbox_publisher_worker.run_forever(
            event_publisher=Mock(),
            session_factory=lambda: session_context,
            stop_event=stop_event,
            sleep=sleep,
        )

    assert session_context.entered == 1
    assert session_context.exited == 1
    run_once.assert_called_once()
    sleep.assert_called_once_with(1.0)


def test_delivery_loop_closes_the_session_before_waiting() -> None:
    stop_event = Event()
    session_context = _SessionContext()
    sleep = Mock(side_effect=lambda _seconds: stop_event.set())

    with patch.object(notification_delivery_worker, "run_listener_once") as run_once:
        notification_delivery_worker.run_forever(
            outbox_consumer=Mock(),
            session_factory=lambda: session_context,
            stop_event=stop_event,
            sleep=sleep,
        )

    assert session_context.entered == 1
    assert session_context.exited == 1
    run_once.assert_called_once()
    sleep.assert_called_once_with(1.0)
