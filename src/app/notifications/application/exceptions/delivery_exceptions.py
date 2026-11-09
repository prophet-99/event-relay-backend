class NotificationAlreadySentException(Exception):
    def __init__(self) -> None:
        super().__init__(
            "The notification has already been sent and the message can be acknowledged."
        )


class NotificationAlreadySendingException(Exception):
    def __init__(self) -> None:
        super().__init__(
            "The notification is already being sent and the message must not be acknowledged."
        )


class NotificationNotFoundException(Exception):
    def __init__(self) -> None:
        super().__init__("The notification was not found in the database")


class NotificationDeliveryException(Exception):
    def __init__(self) -> None:
        super().__init__(
            "The notification delivery process failed, please check the logs"
        )
