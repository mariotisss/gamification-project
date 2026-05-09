from __future__ import annotations

import pytest

from core.pkg.user_system.application.use_cases.user_service import UserService
from core.pkg.user_system.infrastructure.driven.adapters.in_memory_user_repository import (
    InMemoryUserRepository,
)


@pytest.fixture
def user_repo() -> InMemoryUserRepository:
    return InMemoryUserRepository()


@pytest.fixture
def user_service(user_repo: InMemoryUserRepository) -> UserService:
    return UserService(user_repository=user_repo)
