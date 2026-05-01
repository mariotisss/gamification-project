from __future__ import annotations

from uuid import UUID

from core.pkg.reward_system.domain.entities.reward import Reward
from core.pkg.reward_system.domain.ports.driven.reward_repository import RewardRepository


class InMemoryRewardRepository(RewardRepository):
    def __init__(self) -> None:
        self._storage: dict[UUID, Reward] = {}

    def get_by_id(self, reward_id: UUID) -> Reward | None:
        return self._storage.get(reward_id)

    def get_all(self) -> list[Reward]:
        return list(self._storage.values())

    def save(self, reward: Reward) -> Reward:
        self._storage[reward.id] = reward
        return reward
