from __future__ import annotations

from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from core.pkg.reward_system.domain.entities.reward import Reward
from core.pkg.reward_system.infrastructure.driven.adapters.postgres_reward_repository import (
    PostgresRewardRepository,
)
from core.pkg.shared.domain.exceptions.entity_not_found import EntityNotFoundError


def test_given_saved_reward_when_get_by_id_then_returns_same_reward(session: Session) -> None:
    repo = PostgresRewardRepository(session=session)
    reward = Reward(
        name="Coffee mug", description="Branded mug", cost=200, reward_type="merch"
    )
    repo.save(reward=reward)

    result = repo.get_by_id(reward_id=reward.id)

    assert result.name == "Coffee mug"


def test_given_multiple_rewards_when_get_all_then_orders_by_cost(session: Session) -> None:
    repo = PostgresRewardRepository(session=session)
    repo.save(reward=Reward(name="Expensive", description="d", cost=500, reward_type="merch"))
    repo.save(reward=Reward(name="Cheap", description="d", cost=100, reward_type="merch"))

    result = repo.get_all()

    assert [r.name for r in result] == ["Cheap", "Expensive"]


def test_given_unknown_reward_id_when_get_by_id_then_raises_entity_not_found(
    session: Session,
) -> None:
    repo = PostgresRewardRepository(session=session)
    missing_id = uuid4()

    with pytest.raises(expected_exception=EntityNotFoundError) as exc:
        repo.get_by_id(reward_id=missing_id)

    assert exc.value.entity_type == "Reward"
    assert exc.value.entity_id == missing_id
