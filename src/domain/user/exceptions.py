class UserError(Exception):
    """Base exception for all User domain errors."""


class InvalidEmailError(UserError):
    """Raised when an email address fails validation."""

    def __init__(self, email: str):
        super().__init__(f"'{email}' is not a valid email address.")
        self.email = email


class UserAlreadyExistsError(UserError):
    """Raised when attempting to add a user that already exists."""

    def __init__(self, username: str):
        super().__init__(f"User '{username}' already exists.")
        self.username = username


class UserNotFoundError(UserError):
    """Raised when a lookup fails to find a matching user."""

    def __init__(self, identifier: str):
        super().__init__(f"User '{identifier}' was not found.")
        self.identifier = identifier

