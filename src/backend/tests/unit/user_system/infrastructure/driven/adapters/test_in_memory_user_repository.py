from __future__ import annotations

from uuid import uuid4

from core.pkg.user_system.domain.entities.user import User
from core.pkg.user_system.infrastructure.driven.adapters.in_memory_user_repository import (
    InMemoryUserRepository,
)


def test_given_empty_repo_when_get_by_id_then_returns_none() -> None:
    repo = InMemoryUserRepository()

    result = repo.get_by_id(user_id=uuid4())

    assert result is None


def test_given_saved_user_when_get_by_id_then_returns_same_user() -> None:
    repo = InMemoryUserRepository()
    user = User(username="alice", email="a@example.com")
    repo.save(user=user)

    result = repo.get_by_id(user_id=user.id)

    assert result == user


def test_given_multiple_users_when_get_all_then_returns_all() -> None:
    repo = InMemoryUserRepository()
    a = User(username="a", email="a@example.com")
    b = User(username="b", email="b@example.com")
    repo.save(user=a)
    repo.save(user=b)

    result = repo.get_all()

    assert a in result
    assert b in result
    assert len(result) == 2


def test_given_user_when_save_then_returns_saved_user() -> None:
    repo = InMemoryUserRepository()
    user = User(username="alice", email="a@example.com")

    saved = repo.save(user=user)

    assert saved == user


def test_given_existing_user_when_update_then_overwrites_stored_user() -> None:
    repo = InMemoryUserRepository()
    user = User(username="alice", email="a@example.com")
    repo.save(user=user)
    user.add_xp(amount=50)

    repo.update(user=user)

    refreshed = repo.get_by_id(user_id=user.id)
    assert refreshed is not None
    assert refreshed.xp == 50
