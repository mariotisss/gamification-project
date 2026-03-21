from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from core.pkg.gamification_system.domain.entities.mission import Mission
from core.pkg.gamification_system.domain.entities.mission_completion import MissionCompletion


class MissionUseCases(ABC):
    @abstractmethod
    def get_mission(self, mission_id: UUID) -> Mission:
        pass

    @abstractmethod
    def list_active_missions(self) -> list[Mission]:
        pass

    @abstractmethod
    def create_mission(
        self,
        title: str,
        description: str,
        xp_reward: int,
        coin_reward: int,
    ) -> Mission:
        pass

    @abstractmethod
    def complete_mission(self, user_id: UUID, mission_id: UUID) -> MissionCompletion:
        pass
