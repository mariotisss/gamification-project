from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from core.pkg.mission_system.domain.entities.mission import Mission
from core.pkg.shared.domain.entities.mission_completion import MissionCompletion


class MissionRepository(ABC):
    @abstractmethod
    def get_by_id(self, mission_id: UUID) -> Mission | None:
        pass

    @abstractmethod
    def get_all_active(self) -> list[Mission]:
        pass

    @abstractmethod
    def save(self, mission: Mission) -> Mission:
        pass

    @abstractmethod
    def save_completion(self, completion: MissionCompletion) -> MissionCompletion:
        pass

    @abstractmethod
    def get_completions_by_user(self, user_id: UUID) -> list[MissionCompletion]:
        pass
