class DatabaseException(Exception):
    def __init__(self) -> None:
        super().__init__("An error occurred with the database operation")


class NotificationMustFailedStatusException(Exception):
    def __init__(self) -> None:
        super().__init__("The notification must exist and have the FAILED status.")


class NotificationNotFoundException(Exception):
    def __init__(self) -> None:
        super().__init__("The notification doesn't exist.")
