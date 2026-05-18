from __future__ import annotations

from uuid import uuid4

import pytest

from core.pkg.mission_system.domain.entities.mission import Mission
from core.pkg.mission_system.infrastructure.driven.adapters.in_memory_mission_repository import (
    InMemoryMissionRepository,
)
from core.pkg.shared.domain.entities.mission_completion import MissionCompletion
from core.pkg.shared.domain.exceptions.entity_not_found import EntityNotFoundError


def test_given_empty_repo_when_get_by_id_then_raises_entity_not_found() -> None:
    repo = InMemoryMissionRepository()
    missing_id = uuid4()

    with pytest.raises(expected_exception=EntityNotFoundError) as exc:
        repo.get_by_id(mission_id=missing_id)

    assert exc.value.entity_type == "Mission"
    assert exc.value.entity_id == missing_id


def test_given_saved_mission_when_get_by_id_then_returns_same_mission() -> None:
    repo = InMemoryMissionRepository()
    mission = Mission(title="A", description="a", xp_reward=1, coin_reward=1)
    repo.save(mission=mission)

    result = repo.get_by_id(mission_id=mission.id)

    assert result == mission


def test_given_active_and_inactive_missions_when_get_all_active_then_returns_only_active() -> None:
    repo = InMemoryMissionRepository()
    active = Mission(title="A", description="a", xp_reward=1, coin_reward=1)
    inactive = Mission(
        title="B",
        description="b",
        xp_reward=1,
        coin_reward=1,
        is_active=False,
    )
    repo.save(mission=active)
    repo.save(mission=inactive)

    result = repo.get_all_active()

    assert active in result
    assert inactive not in result


def test_given_mission_when_save_then_returns_saved_mission_with_same_id() -> None:
    repo = InMemoryMissionRepository()
    mission = Mission(title="A", description="a", xp_reward=1, coin_reward=1)

    saved = repo.save(mission=mission)

    assert saved.id == mission.id


def test_given_completion_when_save_completion_then_persists_record() -> None:
    repo = InMemoryMissionRepository()
    user_id = uuid4()
    completion = MissionCompletion(user_id=user_id, mission_id=uuid4())

    saved = repo.save_completion(completion=completion)

    assert saved == completion
    assert completion in repo.get_completions_by_user(user_id=user_id)


def test_given_user_with_completions_when_get_completions_by_user_then_returns_only_that_users_records() -> None:
    repo = InMemoryMissionRepository()
    user_a = uuid4()
    user_b = uuid4()
    completion_a = MissionCompletion(user_id=user_a, mission_id=uuid4())
    completion_b = MissionCompletion(user_id=user_b, mission_id=uuid4())
    repo.save_completion(completion=completion_a)
    repo.save_completion(completion=completion_b)

    result = repo.get_completions_by_user(user_id=user_a)

    assert completion_a in result
    assert completion_b not in result


def test_given_user_without_completions_when_get_completions_by_user_then_returns_empty_list() -> None:
    repo = InMemoryMissionRepository()

    result = repo.get_completions_by_user(user_id=uuid4())

    assert result == []
