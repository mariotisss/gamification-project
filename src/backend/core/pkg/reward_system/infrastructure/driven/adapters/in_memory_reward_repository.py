from __future__ import annotations

from uuid import UUID

from core.pkg.reward_system.domain.entities.reward import Reward
from core.pkg.reward_system.domain.ports.driven.reward_repository import RewardRepository
from core.pkg.shared.domain.exceptions.entity_not_found import EntityNotFoundError


class InMemoryRewardRepository(RewardRepository):
    def __init__(self) -> None:
        self._storage: dict[UUID, Reward] = {}

    def get_by_id(self, reward_id: UUID) -> Reward:
        reward = self._storage.get(reward_id)
        if reward is None:
            raise EntityNotFoundError(entity_type="Reward", entity_id=reward_id)
        return reward

    def get_all(self) -> list[Reward]:
        return list(self._storage.values())

    def save(self, reward: Reward) -> Reward:
        self._storage[reward.id] = reward
        return reward
