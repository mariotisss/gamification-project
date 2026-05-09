from __future__ import annotations

import pytest

from core.pkg.reward_system.application.use_cases.reward_service import RewardService
from core.pkg.reward_system.domain.entities.reward import Reward
from core.pkg.reward_system.infrastructure.driven.adapters.in_memory_reward_repository import (
    InMemoryRewardRepository,
)
from core.pkg.user_system.domain.entities.user import User
from core.pkg.user_system.infrastructure.driven.adapters.in_memory_user_repository import (
    InMemoryUserRepository,
)


@pytest.fixture
def reward_repo() -> InMemoryRewardRepository:
    return InMemoryRewardRepository()


@pytest.fixture
def user_repo() -> InMemoryUserRepository:
    return InMemoryUserRepository()


@pytest.fixture
def reward_service(
    reward_repo: InMemoryRewardRepository,
    user_repo: InMemoryUserRepository,
) -> RewardService:
    return RewardService(reward_repository=reward_repo, user_repository=user_repo)


@pytest.fixture
def seeded_user(user_repo: InMemoryUserRepository) -> User:
    user = User(username="bob", email="bob@example.com")
    user.add_dev_coins(amount=100)
    return user_repo.save(user=user)


@pytest.fixture
def seeded_reward(reward_repo: InMemoryRewardRepository) -> Reward:
    reward = Reward(name="Sticker", description="cool", cost=30, reward_type="cosmetic")
    return reward_repo.save(reward=reward)
