class InvalidCredentialsException(Exception):
    def __init__(self) -> None:
        super().__init__("The credentials are invalid!!")


class PasswordChangeRequiredException(Exception):
    def __init__(self) -> None:
        super().__init__("You must change your temporary password before continuing.")


class DatabaseOperationException(Exception):
    def __init__(self) -> None:
        super().__init__("An unexpected error ocurred, please try again later.")
