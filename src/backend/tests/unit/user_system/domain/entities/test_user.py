from __future__ import annotations

from datetime import timezone

import pytest

from core.pkg.user_system.domain.entities.user import User


def test_given_default_user_when_instantiated_then_has_zero_xp_level_one_zero_coins() -> None:
    user = User(username="alice", email="a@example.com")

    assert user.xp == 0
    assert user.level == 1
    assert user.dev_coins == 0


def test_given_user_when_add_xp_with_positive_amount_then_xp_increases() -> None:
    user = User(username="alice", email="a@example.com")

    user.add_xp(amount=30)

    assert user.xp == 30


def test_given_user_when_add_xp_crosses_100_threshold_then_level_increments() -> None:
    user = User(username="alice", email="a@example.com")

    user.add_xp(amount=100)

    assert user.level == 2


def test_given_user_when_add_xp_crosses_multiple_thresholds_then_level_calculated_correctly() -> None:
    user = User(username="alice", email="a@example.com")

    user.add_xp(amount=250)

    assert user.xp == 250
    assert user.level == 3


def test_given_user_when_add_xp_with_negative_amount_then_raises_value_error() -> None:
    user = User(username="alice", email="a@example.com")

    with pytest.raises(expected_exception=ValueError):
        user.add_xp(amount=-1)


def test_given_user_when_add_dev_coins_with_positive_amount_then_balance_increases() -> None:
    user = User(username="alice", email="a@example.com")

    user.add_dev_coins(amount=15)

    assert user.dev_coins == 15


def test_given_user_when_add_dev_coins_with_negative_amount_then_raises_value_error() -> None:
    user = User(username="alice", email="a@example.com")

    with pytest.raises(expected_exception=ValueError):
        user.add_dev_coins(amount=-1)


def test_given_user_when_deduct_dev_coins_within_balance_then_balance_decreases() -> None:
    user = User(username="alice", email="a@example.com")
    user.add_dev_coins(amount=20)

    user.deduct_dev_coins(amount=5)

    assert user.dev_coins == 15


def test_given_user_when_deduct_dev_coins_exceeding_balance_then_raises_value_error() -> None:
    user = User(username="alice", email="a@example.com")
    user.add_dev_coins(amount=5)

    with pytest.raises(expected_exception=ValueError):
        user.deduct_dev_coins(amount=10)


def test_given_user_when_deduct_dev_coins_with_negative_amount_then_raises_value_error() -> None:
    user = User(username="alice", email="a@example.com")

    with pytest.raises(expected_exception=ValueError):
        user.deduct_dev_coins(amount=-1)


def test_given_user_when_instantiated_then_created_at_is_utc() -> None:
    user = User(username="alice", email="a@example.com")

    assert user.created_at.tzinfo is not None
    assert user.created_at.utcoffset() == timezone.utc.utcoffset(None)
