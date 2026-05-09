from __future__ import annotations

import pytest

from core.pkg.mission_system.application.use_cases.mission_service import MissionService
from core.pkg.mission_system.domain.entities.mission import Mission
from core.pkg.mission_system.infrastructure.driven.adapters.in_memory_mission_repository import (
    InMemoryMissionRepository,
)
from core.pkg.user_system.domain.entities.user import User
from core.pkg.user_system.infrastructure.driven.adapters.in_memory_user_repository import (
    InMemoryUserRepository,
)


@pytest.fixture
def mission_repo() -> InMemoryMissionRepository:
    return InMemoryMissionRepository()


@pytest.fixture
def user_repo() -> InMemoryUserRepository:
    return InMemoryUserRepository()


@pytest.fixture
def mission_service(
    mission_repo: InMemoryMissionRepository,
    user_repo: InMemoryUserRepository,
) -> MissionService:
    return MissionService(mission_repository=mission_repo, user_repository=user_repo)


@pytest.fixture
def seeded_user(user_repo: InMemoryUserRepository) -> User:
    user = User(username="alice", email="alice@example.com")
    return user_repo.save(user=user)


@pytest.fixture
def seeded_mission(mission_repo: InMemoryMissionRepository) -> Mission:
    mission = Mission(
        title="First Mission",
        description="Do the thing",
        xp_reward=50,
        coin_reward=10,
    )
    return mission_repo.save(mission=mission)
