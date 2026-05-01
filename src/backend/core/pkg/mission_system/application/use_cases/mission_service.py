from __future__ import annotations

from uuid import UUID

from core.pkg.mission_system.domain.entities.mission import Mission
from core.pkg.mission_system.domain.exceptions.mission_already_completed import MissionAlreadyCompletedError
from core.pkg.mission_system.domain.ports.driven.mission_repository import MissionRepository
from core.pkg.mission_system.domain.ports.driving.mission_use_cases import MissionUseCases
from core.pkg.shared.domain.entities.mission_completion import MissionCompletion
from core.pkg.shared.domain.exceptions.entity_not_found import EntityNotFoundError
from core.pkg.user_system.domain.ports.driven.user_repository import UserRepository


class MissionService(MissionUseCases):
    def __init__(
        self,
        mission_repository: MissionRepository,
        user_repository: UserRepository,
    ) -> None:
        self._mission_repo = mission_repository
        self._user_repo = user_repository

    def get_mission(self, mission_id: UUID) -> Mission:
        mission = self._mission_repo.get_by_id(mission_id=mission_id)
        if mission is None:
            raise EntityNotFoundError(entity_type="Mission", entity_id=mission_id)
        return mission

    def list_active_missions(self) -> list[Mission]:
        return self._mission_repo.get_all_active()

    def create_mission(
        self,
        title: str,
        description: str,
        xp_reward: int,
        coin_reward: int,
    ) -> Mission:
        mission = Mission(
            title=title,
            description=description,
            xp_reward=xp_reward,
            coin_reward=coin_reward,
        )
        return self._mission_repo.save(mission=mission)

    def complete_mission(self, user_id: UUID, mission_id: UUID) -> MissionCompletion:
        user = self._user_repo.get_by_id(user_id=user_id)
        if user is None:
            raise EntityNotFoundError(entity_type="User", entity_id=user_id)

        mission = self._mission_repo.get_by_id(mission_id=mission_id)
        if mission is None:
            raise EntityNotFoundError(entity_type="Mission", entity_id=mission_id)

        existing = self._mission_repo.get_completions_by_user(user_id=user_id)
        if any(c.mission_id == mission_id for c in existing):
            raise MissionAlreadyCompletedError(user_id=user_id, mission_id=mission_id)

        user.add_xp(amount=mission.xp_reward)
        user.add_dev_coins(amount=mission.coin_reward)
        self._user_repo.update(user=user)

        completion = MissionCompletion(user_id=user_id, mission_id=mission_id)
        return self._mission_repo.save_completion(completion=completion)
