from __future__ import annotations

from uuid import uuid4

from core.pkg.reward_system.domain.exceptions.insufficient_coins import InsufficientCoinsError


def test_given_required_and_available_when_raised_then_message_includes_both_amounts() -> None:
    user_id = uuid4()

    error = InsufficientCoinsError(user_id=user_id, required=100, available=20)

    assert "100" in str(error)
    assert "20" in str(error)
    assert error.required == 100
    assert error.available == 20


def test_given_exception_when_caught_then_is_subclass_of_exception() -> None:
    assert issubclass(InsufficientCoinsError, Exception)
