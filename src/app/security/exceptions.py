class InvalidTokenException(Exception):
    def __init__(self) -> None:
        super().__init__("Your access token is invalid. Please sign in again")


class RequiredClaimsTokenException(Exception):
    def __init__(self) -> None:
        super().__init__("Your access token is missing required claims.")


class ExpiredAccessTokenException(Exception):
    def __init__(self) -> None:
        super().__init__("Your session has expired. Please sign in again.")
