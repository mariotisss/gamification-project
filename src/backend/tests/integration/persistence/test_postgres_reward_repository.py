from __future__ import annotations

from uuid import uuid4

from sqlalchemy.orm import Session

from core.pkg.reward_system.domain.entities.reward import Reward
from core.pkg.reward_system.infrastructure.driven.adapters.postgres_reward_repository import (
    PostgresRewardRepository,
)


def test_given_saved_reward_when_get_by_id_then_returns_same_reward(session: Session) -> None:
    repo = PostgresRewardRepository(session=session)
    reward = Reward(
        name="Coffee mug", description="Branded mug", cost=200, reward_type="merch"
    )
    repo.save(reward=reward)

    result = repo.get_by_id(reward_id=reward.id)

    assert result is not None
    assert result.name == "Coffee mug"


def test_given_multiple_rewards_when_get_all_then_orders_by_cost(session: Session) -> None:
    repo = PostgresRewardRepository(session=session)
    repo.save(reward=Reward(name="Expensive", description="d", cost=500, reward_type="merch"))
    repo.save(reward=Reward(name="Cheap", description="d", cost=100, reward_type="merch"))

    result = repo.get_all()

    assert [r.name for r in result] == ["Cheap", "Expensive"]


def test_given_unknown_reward_id_when_get_by_id_then_returns_none(session: Session) -> None:
    repo = PostgresRewardRepository(session=session)

    result = repo.get_by_id(reward_id=uuid4())

    assert result is None
