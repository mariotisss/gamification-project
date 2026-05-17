from __future__ import annotations


class UserAlreadyExistsError(Exception):
    def __init__(self, username: str, email: str) -> None:
        self.username = username
        self.email = email
        super().__init__(
            f"A user with username '{username}' or email '{email}' already exists"
        )
