from __future__ import annotations

from uuid import uuid4

import pytest

from core.pkg.mission_system.application.use_cases.mission_service import MissionService
from core.pkg.mission_system.domain.entities.mission import Mission
from core.pkg.mission_system.domain.exceptions.mission_already_completed import (
    MissionAlreadyCompletedError,
)
from core.pkg.mission_system.infrastructure.driven.adapters.in_memory_mission_repository import (
    InMemoryMissionRepository,
)
from core.pkg.shared.domain.entities.mission_completion import MissionCompletion
from core.pkg.shared.domain.exceptions.entity_not_found import EntityNotFoundError
from core.pkg.user_system.domain.entities.user import User
from core.pkg.user_system.infrastructure.driven.adapters.in_memory_user_repository import (
    InMemoryUserRepository,
)


def test_given_existing_mission_when_get_mission_then_returns_mission(
    mission_service: MissionService,
    seeded_mission: Mission,
) -> None:
    result = mission_service.get_mission(mission_id=seeded_mission.id)

    assert result == seeded_mission


def test_given_missing_mission_when_get_mission_then_raises_entity_not_found(
    mission_service: MissionService,
) -> None:
    with pytest.raises(expected_exception=EntityNotFoundError) as exc_info:
        mission_service.get_mission(mission_id=uuid4())

    assert exc_info.value.entity_type == "Mission"


def test_given_active_and_inactive_missions_when_list_active_missions_then_returns_only_active(
    mission_service: MissionService,
    mission_repo: InMemoryMissionRepository,
) -> None:
    active = Mission(title="A", description="a", xp_reward=1, coin_reward=1)
    inactive = Mission(
        title="B",
        description="b",
        xp_reward=1,
        coin_reward=1,
        is_active=False,
    )
    mission_repo.save(mission=active)
    mission_repo.save(mission=inactive)

    result = mission_service.list_active_missions()

    assert active in result
    assert inactive not in result


def test_given_valid_input_when_create_mission_then_persists_and_returns_mission(
    mission_service: MissionService,
    mission_repo: InMemoryMissionRepository,
) -> None:
    created = mission_service.create_mission(
        title="New",
        description="New desc",
        xp_reward=20,
        coin_reward=5,
    )

    assert created.title == "New"
    assert mission_repo.get_by_id(mission_id=created.id) == created


def test_given_unknown_user_when_complete_mission_then_raises_entity_not_found_for_user(
    mission_service: MissionService,
    seeded_mission: Mission,
) -> None:
    with pytest.raises(expected_exception=EntityNotFoundError) as exc_info:
        mission_service.complete_mission(user_id=uuid4(), mission_id=seeded_mission.id)

    assert exc_info.value.entity_type == "User"


def test_given_unknown_mission_when_complete_mission_then_raises_entity_not_found_for_mission(
    mission_service: MissionService,
    seeded_user: User,
) -> None:
    with pytest.raises(expected_exception=EntityNotFoundError) as exc_info:
        mission_service.complete_mission(user_id=seeded_user.id, mission_id=uuid4())

    assert exc_info.value.entity_type == "Mission"


def test_given_already_completed_when_complete_mission_then_raises_mission_already_completed(
    mission_service: MissionService,
    seeded_user: User,
    seeded_mission: Mission,
) -> None:
    mission_service.complete_mission(user_id=seeded_user.id, mission_id=seeded_mission.id)

    with pytest.raises(expected_exception=MissionAlreadyCompletedError):
        mission_service.complete_mission(user_id=seeded_user.id, mission_id=seeded_mission.id)


def test_given_valid_completion_when_complete_mission_then_awards_xp_and_coins_to_user(
    mission_service: MissionService,
    seeded_user: User,
    seeded_mission: Mission,
) -> None:
    starting_xp = seeded_user.xp
    starting_coins = seeded_user.dev_coins

    mission_service.complete_mission(user_id=seeded_user.id, mission_id=seeded_mission.id)

    assert seeded_user.xp == starting_xp + seeded_mission.xp_reward
    assert seeded_user.dev_coins == starting_coins + seeded_mission.coin_reward


def test_given_valid_completion_when_complete_mission_then_persists_completion_record(
    mission_service: MissionService,
    mission_repo: InMemoryMissionRepository,
    seeded_user: User,
    seeded_mission: Mission,
) -> None:
    completion = mission_service.complete_mission(
        user_id=seeded_user.id,
        mission_id=seeded_mission.id,
    )

    persisted = mission_repo.get_completions_by_user(user_id=seeded_user.id)
    assert isinstance(completion, MissionCompletion)
    assert completion in persisted


def test_given_valid_completion_when_complete_mission_then_updates_user_in_repository(
    mission_service: MissionService,
    user_repo: InMemoryUserRepository,
    seeded_user: User,
    seeded_mission: Mission,
) -> None:
    mission_service.complete_mission(user_id=seeded_user.id, mission_id=seeded_mission.id)

    refreshed = user_repo.get_by_id(user_id=seeded_user.id)
    assert refreshed is not None
    assert refreshed.xp == seeded_mission.xp_reward
    assert refreshed.dev_coins == seeded_mission.coin_reward
