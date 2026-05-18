from __future__ import annotations

from uuid import uuid4

from core.pkg.user_system.domain.exceptions.concurrent_user_update import (
    ConcurrentUserUpdateError,
)


def test_given_user_id_when_error_constructed_then_carries_user_id_and_message() -> None:
    user_id = uuid4()

    error = ConcurrentUserUpdateError(user_id=user_id)

    assert error.user_id == user_id
    assert str(user_id) in str(error)
    assert "concurrently" in str(error)
