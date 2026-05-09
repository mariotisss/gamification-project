from __future__ import annotations

from uuid import uuid4

import pytest

from core.pkg.reward_system.application.use_cases.reward_service import RewardService
from core.pkg.reward_system.domain.entities.reward import Reward
from core.pkg.reward_system.domain.exceptions.insufficient_coins import InsufficientCoinsError
from core.pkg.reward_system.infrastructure.driven.adapters.in_memory_reward_repository import (
    InMemoryRewardRepository,
)
from core.pkg.shared.domain.exceptions.entity_not_found import EntityNotFoundError
from core.pkg.user_system.domain.entities.user import User
from core.pkg.user_system.infrastructure.driven.adapters.in_memory_user_repository import (
    InMemoryUserRepository,
)


def test_given_existing_reward_when_get_reward_then_returns_reward(
    reward_service: RewardService,
    seeded_reward: Reward,
) -> None:
    result = reward_service.get_reward(reward_id=seeded_reward.id)

    assert result == seeded_reward


def test_given_missing_reward_when_get_reward_then_raises_entity_not_found(
    reward_service: RewardService,
) -> None:
    with pytest.raises(expected_exception=EntityNotFoundError) as exc_info:
        reward_service.get_reward(reward_id=uuid4())

    assert exc_info.value.entity_type == "Reward"


def test_given_rewards_when_list_rewards_then_returns_all(
    reward_service: RewardService,
    reward_repo: InMemoryRewardRepository,
) -> None:
    a = Reward(name="A", description="a", cost=1, reward_type="cosmetic")
    b = Reward(name="B", description="b", cost=2, reward_type="cosmetic")
    reward_repo.save(reward=a)
    reward_repo.save(reward=b)

    result = reward_service.list_rewards()

    assert a in result
    assert b in result


def test_given_valid_input_when_create_reward_then_persists_and_returns_reward(
    reward_service: RewardService,
    reward_repo: InMemoryRewardRepository,
) -> None:
    created = reward_service.create_reward(
        name="N",
        description="D",
        cost=15,
        reward_type="cosmetic",
    )

    assert created.name == "N"
    assert reward_repo.get_by_id(reward_id=created.id) == created


def test_given_unknown_user_when_purchase_reward_then_raises_entity_not_found_for_user(
    reward_service: RewardService,
    seeded_reward: Reward,
) -> None:
    with pytest.raises(expected_exception=EntityNotFoundError) as exc_info:
        reward_service.purchase_reward(user_id=uuid4(), reward_id=seeded_reward.id)

    assert exc_info.value.entity_type == "User"


def test_given_unknown_reward_when_purchase_reward_then_raises_entity_not_found_for_reward(
    reward_service: RewardService,
    seeded_user: User,
) -> None:
    with pytest.raises(expected_exception=EntityNotFoundError) as exc_info:
        reward_service.purchase_reward(user_id=seeded_user.id, reward_id=uuid4())

    assert exc_info.value.entity_type == "Reward"


def test_given_insufficient_coins_when_purchase_reward_then_raises_insufficient_coins(
    reward_service: RewardService,
    user_repo: InMemoryUserRepository,
    reward_repo: InMemoryRewardRepository,
) -> None:
    poor = User(username="poor", email="p@example.com")
    user_repo.save(user=poor)
    expensive = Reward(name="X", description="x", cost=100, reward_type="cosmetic")
    reward_repo.save(reward=expensive)

    with pytest.raises(expected_exception=InsufficientCoinsError):
        reward_service.purchase_reward(user_id=poor.id, reward_id=expensive.id)


def test_given_sufficient_coins_when_purchase_reward_then_deducts_coins_and_returns_reward(
    reward_service: RewardService,
    seeded_user: User,
    seeded_reward: Reward,
) -> None:
    starting = seeded_user.dev_coins

    result = reward_service.purchase_reward(
        user_id=seeded_user.id,
        reward_id=seeded_reward.id,
    )

    assert result == seeded_reward
    assert seeded_user.dev_coins == starting - seeded_reward.cost


def test_given_sufficient_coins_when_purchase_reward_then_updates_user_in_repository(
    reward_service: RewardService,
    user_repo: InMemoryUserRepository,
    seeded_user: User,
    seeded_reward: Reward,
) -> None:
    starting = seeded_user.dev_coins

    reward_service.purchase_reward(user_id=seeded_user.id, reward_id=seeded_reward.id)

    refreshed = user_repo.get_by_id(user_id=seeded_user.id)
    assert refreshed is not None
    assert refreshed.dev_coins == starting - seeded_reward.cost
