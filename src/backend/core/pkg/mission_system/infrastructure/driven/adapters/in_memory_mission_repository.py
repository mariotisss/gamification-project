from __future__ import annotations

from uuid import UUID

from core.pkg.mission_system.domain.entities.mission import Mission
from core.pkg.mission_system.domain.ports.driven.mission_repository import MissionRepository
from core.pkg.shared.domain.entities.mission_completion import MissionCompletion


class InMemoryMissionRepository(MissionRepository):
    def __init__(self) -> None:
        self._missions: dict[UUID, Mission] = {}
        self._completions: list[MissionCompletion] = []

    def get_by_id(self, mission_id: UUID) -> Mission | None:
        return self._missions.get(mission_id)

    def get_all_active(self) -> list[Mission]:
        return [m for m in self._missions.values() if m.is_active]

    def save(self, mission: Mission) -> Mission:
        self._missions[mission.id] = mission
        return mission

    def save_completion(self, completion: MissionCompletion) -> MissionCompletion:
        self._completions.append(completion)
        return completion

    def get_completions_by_user(self, user_id: UUID) -> list[MissionCompletion]:
        return [c for c in self._completions if c.user_id == user_id]
