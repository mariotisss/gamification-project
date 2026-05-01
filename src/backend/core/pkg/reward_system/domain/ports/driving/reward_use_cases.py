from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from core.pkg.reward_system.domain.entities.reward import Reward


class RewardUseCases(ABC):
    @abstractmethod
    def get_reward(self, reward_id: UUID) -> Reward:
        pass

    @abstractmethod
    def list_rewards(self) -> list[Reward]:
        pass

    @abstractmethod
    def create_reward(
        self,
        name: str,
        description: str,
        cost: int,
        reward_type: str,
    ) -> Reward:
        pass

    @abstractmethod
    def purchase_reward(self, user_id: UUID, reward_id: UUID) -> Reward:
        pass
