from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from core.pkg.mission_system.domain.entities.mission import Mission
from core.pkg.mission_system.domain.exceptions.mission_already_completed import (
    MissionAlreadyCompletedError,
)
from core.pkg.mission_system.infrastructure.driven.adapters.postgres_mission_repository import (
    PostgresMissionRepository,
)
from core.pkg.shared.domain.entities.mission_completion import MissionCompletion
from core.pkg.user_system.domain.entities.user import User
from core.pkg.user_system.infrastructure.driven.adapters.postgres_user_repository import (
    PostgresUserRepository,
)


def test_given_saved_mission_when_get_by_id_then_returns_same_mission(session: Session) -> None:
    repo = PostgresMissionRepository(session=session)
    mission = Mission(
        title="Refactor module",
        description="Refactor the auth module",
        xp_reward=100,
        coin_reward=50,
    )
    repo.save(mission=mission)

    result = repo.get_by_id(mission_id=mission.id)

    assert result is not None
    assert result.title == "Refactor module"


def test_given_active_and_inactive_missions_when_get_all_active_then_only_active(
    session: Session,
) -> None:
    repo = PostgresMissionRepository(session=session)
    repo.save(
        mission=Mission(
            title="Active", description="d", xp_reward=10, coin_reward=5, is_active=True
        )
    )
    repo.save(
        mission=Mission(
            title="Inactive", description="d", xp_reward=10, coin_reward=5, is_active=False
        )
    )

    result = repo.get_all_active()

    assert len(result) == 1
    assert result[0].title == "Active"


def test_given_completion_saved_when_get_completions_by_user_then_returns_it(
    session: Session,
) -> None:
    user_repo = PostgresUserRepository(session=session)
    mission_repo = PostgresMissionRepository(session=session)

    user = user_repo.save(user=User(username="alice", email="a@example.com"))
    mission = mission_repo.save(
        mission=Mission(title="t", description="d", xp_reward=10, coin_reward=5)
    )

    completion = MissionCompletion(user_id=user.id, mission_id=mission.id)
    mission_repo.save_completion(completion=completion)

    result = mission_repo.get_completions_by_user(user_id=user.id)

    assert len(result) == 1
    assert result[0].mission_id == mission.id


def test_given_duplicate_completion_when_save_then_raises_already_completed(
    session: Session,
) -> None:
    user_repo = PostgresUserRepository(session=session)
    mission_repo = PostgresMissionRepository(session=session)

    user = user_repo.save(user=User(username="alice", email="a@example.com"))
    mission = mission_repo.save(
        mission=Mission(title="t", description="d", xp_reward=10, coin_reward=5)
    )

    mission_repo.save_completion(
        completion=MissionCompletion(user_id=user.id, mission_id=mission.id)
    )

    with pytest.raises(expected_exception=MissionAlreadyCompletedError):
        mission_repo.save_completion(
            completion=MissionCompletion(user_id=user.id, mission_id=mission.id)
        )


def test_given_unknown_mission_id_when_get_by_id_then_returns_none(session: Session) -> None:
    repo = PostgresMissionRepository(session=session)

    result = repo.get_by_id(mission_id=uuid4())

    assert result is None
