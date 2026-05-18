from __future__ import annotations

from uuid import UUID


class ConcurrentUserUpdateError(Exception):
    def __init__(self, user_id: UUID) -> None:
        self.user_id = user_id
        super().__init__(
            f"User '{user_id}' was modified concurrently; the update was rejected."
        )
