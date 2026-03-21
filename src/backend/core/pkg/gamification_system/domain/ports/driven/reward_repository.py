from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from core.pkg.gamification_system.domain.entities.reward import Reward


class RewardRepository(ABC):
    @abstractmethod
    def get_by_id(self, reward_id: UUID) -> Reward | None:
        pass

    @abstractmethod
    def get_all(self) -> list[Reward]:
        pass

    @abstractmethod
    def save(self, reward: Reward) -> Reward:
        pass
