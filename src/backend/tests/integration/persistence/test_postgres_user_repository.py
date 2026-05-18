from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy import Engine
from sqlalchemy.orm import Session

from core.infrastructure.persistence.database import build_session_factory
from core.pkg.shared.domain.exceptions.entity_not_found import EntityNotFoundError
from core.pkg.user_system.domain.entities.user import User
from core.pkg.user_system.domain.exceptions.concurrent_user_update import (
    ConcurrentUserUpdateError,
)
from core.pkg.user_system.infrastructure.driven.adapters.postgres_user_repository import (
    PostgresUserRepository,
)


def test_given_saved_user_when_get_by_id_then_returns_same_user(session: Session) -> None:
    repo = PostgresUserRepository(session=session)
    user = User(username="alice", email="a@example.com")
    repo.save(user=user)

    result = repo.get_by_id(user_id=user.id)

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
    assert refreshed.xp == 150
    assert refreshed.level == 2


def test_given_unknown_id_when_get_by_id_then_raises_entity_not_found(session: Session) -> None:
    repo = PostgresUserRepository(session=session)
    missing_id = uuid4()

    with pytest.raises(expected_exception=EntityNotFoundError) as exc:
        repo.get_by_id(user_id=missing_id)

    assert exc.value.entity_type == "User"
    assert exc.value.entity_id == missing_id


def test_given_stale_version_when_update_then_raises_concurrent_user_update(
    engine: Engine,
) -> None:
    factory = build_session_factory(engine=engine)

    with factory() as setup_session:
        user = User(username="alice", email="a@example.com")
        PostgresUserRepository(session=setup_session).save(user=user)
        setup_session.commit()

    try:
        with factory() as session_b, factory() as session_c:
            user_b = PostgresUserRepository(session=session_b).get_by_id(user_id=user.id)
            user_c = PostgresUserRepository(session=session_c).get_by_id(user_id=user.id)

            user_b.add_dev_coins(amount=10)
            PostgresUserRepository(session=session_b).update(user=user_b)
            session_b.commit()

            user_c.add_dev_coins(amount=5)
            with pytest.raises(expected_exception=ConcurrentUserUpdateError) as exc:
                PostgresUserRepository(session=session_c).update(user=user_c)

            assert exc.value.user_id == user.id
    finally:
        with factory() as cleanup_session:
            from core.pkg.user_system.infrastructure.driven.persistence.models.user_model import (
                UserModel,
            )

            cleanup_session.query(UserModel).delete()
            cleanup_session.commit()
