from __future__ import annotations

from sqlalchemy.orm import Session

from core.pkg.user_system.domain.entities.user import User
from core.pkg.user_system.infrastructure.driven.adapters.postgres_user_repository import (
    PostgresUserRepository,
)


def test_given_saved_user_when_get_by_id_then_returns_same_user(session: Session) -> None:
    repo = PostgresUserRepository(session=session)
    user = User(username="alice", email="a@example.com")
    repo.save(user=user)

    result = repo.get_by_id(user_id=user.id)

    assert result is not None
    assert result.username == "alice"
    assert result.email == "a@example.com"


def test_given_no_users_when_get_all_then_returns_empty(session: Session) -> None:
    repo = PostgresUserRepository(session=session)

    result = repo.get_all()

    assert result == []


def test_given_multiple_users_when_get_all_then_returns_all(session: Session) -> None:
    repo = PostgresUserRepository(session=session)
    repo.save(user=User(username="alice", email="a@example.com"))
    repo.save(user=User(username="bob", email="b@example.com"))

    result = repo.get_all()

    assert len(result) == 2


def test_given_user_with_xp_when_update_then_persists_changes(session: Session) -> None:
    repo = PostgresUserRepository(session=session)
    user = User(username="alice", email="a@example.com")
    repo.save(user=user)
    user.add_xp(amount=150)

    repo.update(user=user)

    refreshed = repo.get_by_id(user_id=user.id)
    assert refreshed is not None
    assert refreshed.xp == 150
    assert refreshed.level == 2


def test_given_unknown_id_when_get_by_id_then_returns_none(session: Session) -> None:
    from uuid import uuid4

    repo = PostgresUserRepository(session=session)

    result = repo.get_by_id(user_id=uuid4())

    assert result is None
