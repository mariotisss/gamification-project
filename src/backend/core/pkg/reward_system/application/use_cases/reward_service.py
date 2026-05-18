from __future__ import annotations

from uuid import UUID

from core.pkg.reward_system.domain.entities.reward import Reward
from core.pkg.reward_system.domain.exceptions.insufficient_coins import InsufficientCoinsError
from core.pkg.reward_system.domain.ports.driven.reward_repository import RewardRepository
from core.pkg.reward_system.domain.ports.driving.reward_use_cases import RewardUseCases
from core.pkg.user_system.domain.ports.driven.user_repository import UserRepository


class RewardService(RewardUseCases):
    def __init__(
        self,
        reward_repository: RewardRepository,
        user_repository: UserRepository,
    ) -> None:
        self._reward_repo = reward_repository
        self._user_repo = user_repository

    def get_reward(self, reward_id: UUID) -> Reward:
        return self._reward_repo.get_by_id(reward_id=reward_id)

    def list_rewards(self) -> list[Reward]:
        return self._reward_repo.get_all()

    def create_reward(
        self,
        name: str,
        description: str,
        cost: int,
        reward_type: str,
    ) -> Reward:
        reward = Reward(
            name=name,
            description=description,
            cost=cost,
            reward_type=reward_type,
        )
        return self._reward_repo.save(reward=reward)

    def purchase_reward(self, user_id: UUID, reward_id: UUID) -> Reward:
        user = self._user_repo.get_by_id(user_id=user_id)
        reward = self._reward_repo.get_by_id(reward_id=reward_id)

        if user.dev_coins < reward.cost:
            raise InsufficientCoinsError(user_id=user_id, required=reward.cost, available=user.dev_coins)

        user.deduct_dev_coins(amount=reward.cost)
        self._user_repo.update(user=user)

        return reward
