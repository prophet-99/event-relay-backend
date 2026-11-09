class DatabaseException(Exception):
    def __init__(self) -> None:
        super().__init__("An error occurred with the database operation")
