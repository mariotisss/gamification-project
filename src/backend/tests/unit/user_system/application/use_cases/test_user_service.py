from __future__ import annotations

from uuid import uuid4

import pytest

from core.pkg.shared.domain.exceptions.entity_not_found import EntityNotFoundError
from core.pkg.user_system.application.use_cases.user_service import UserService
from core.pkg.user_system.domain.entities.user import User
from core.pkg.user_system.infrastructure.driven.adapters.in_memory_user_repository import (
    InMemoryUserRepository,
)


def test_given_existing_user_when_get_user_then_returns_user(
    user_service: UserService,
    user_repo: InMemoryUserRepository,
) -> None:
    user = User(username="alice", email="a@example.com")
    user_repo.save(user=user)

    result = user_service.get_user(user_id=user.id)

    assert result == user


def test_given_missing_user_when_get_user_then_raises_entity_not_found(
    user_service: UserService,
) -> None:
    with pytest.raises(expected_exception=EntityNotFoundError) as exc_info:
        user_service.get_user(user_id=uuid4())

    assert exc_info.value.entity_type == "User"


def test_given_users_when_list_users_then_returns_all(
    user_service: UserService,
    user_repo: InMemoryUserRepository,
) -> None:
    a = User(username="a", email="a@example.com")
    b = User(username="b", email="b@example.com")
    user_repo.save(user=a)
    user_repo.save(user=b)

    result = user_service.list_users()

    assert a in result
    assert b in result


def test_given_valid_input_when_create_user_then_persists_with_default_xp_level_coins(
    user_service: UserService,
    user_repo: InMemoryUserRepository,
) -> None:
    created = user_service.create_user(username="alice", email="a@example.com")

    assert created.xp == 0
    assert created.level == 1
    assert created.dev_coins == 0
    assert user_repo.get_by_id(user_id=created.id) == created
