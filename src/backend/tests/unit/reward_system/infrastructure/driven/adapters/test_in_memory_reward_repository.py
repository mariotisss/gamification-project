from __future__ import annotations

from uuid import uuid4

from core.pkg.reward_system.domain.entities.reward import Reward
from core.pkg.reward_system.infrastructure.driven.adapters.in_memory_reward_repository import (
    InMemoryRewardRepository,
)


def test_given_empty_repo_when_get_by_id_then_returns_none() -> None:
    repo = InMemoryRewardRepository()

    result = repo.get_by_id(reward_id=uuid4())

    assert result is None


def test_given_saved_reward_when_get_by_id_then_returns_same_reward() -> None:
    repo = InMemoryRewardRepository()
    reward = Reward(name="N", description="D", cost=10, reward_type="cosmetic")
    repo.save(reward=reward)

    result = repo.get_by_id(reward_id=reward.id)

    assert result == reward


def test_given_multiple_rewards_when_get_all_then_returns_all() -> None:
    repo = InMemoryRewardRepository()
    a = Reward(name="A", description="a", cost=1, reward_type="cosmetic")
    b = Reward(name="B", description="b", cost=2, reward_type="cosmetic")
    repo.save(reward=a)
    repo.save(reward=b)

    result = repo.get_all()

    assert a in result
    assert b in result
    assert len(result) == 2


def test_given_reward_when_save_then_returns_saved_reward_with_same_id() -> None:
    repo = InMemoryRewardRepository()
    reward = Reward(name="N", description="D", cost=10, reward_type="cosmetic")

    saved = repo.save(reward=reward)

    assert saved.id == reward.id
