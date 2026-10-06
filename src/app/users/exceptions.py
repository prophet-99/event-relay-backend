class DatabaseOperationException(Exception):
    def __init__(self) -> None:
        super().__init__("An error occurred during the database operation.")


class UserNotFoundException(Exception):
    def __init__(self, user_id: int) -> None:
        super().__init__(f"The user with {user_id} didnt match the search criteria.")
        self.user_id = user_id


class UserEmailAlreadyTakenException(Exception):
    def __init__(self, email: str) -> None:
        super().__init__(f"The user with email: {email} is already taken.")
        self.email = email
