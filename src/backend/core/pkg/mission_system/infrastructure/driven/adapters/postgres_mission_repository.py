from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from core.pkg.mission_system.domain.entities.mission import Mission
from core.pkg.mission_system.domain.exceptions.mission_already_completed import (
    MissionAlreadyCompletedError,
)
from core.pkg.mission_system.domain.ports.driven.mission_repository import MissionRepository
from core.pkg.mission_system.infrastructure.driven.persistence.models.mission_completion_model import (
    MissionCompletionModel,
)
from core.pkg.mission_system.infrastructure.driven.persistence.models.mission_model import (
    MissionModel,
)
from core.pkg.shared.domain.entities.mission_completion import MissionCompletion


def _mission_to_domain(model: MissionModel) -> Mission:
    return Mission(
        title=model.title,
        description=model.description,
        xp_reward=model.xp_reward,
        coin_reward=model.coin_reward,
        id=model.id,
        is_active=model.is_active,
    )


def _mission_to_model(entity: Mission) -> MissionModel:
    return MissionModel(
        id=entity.id,
        title=entity.title,
        description=entity.description,
        xp_reward=entity.xp_reward,
        coin_reward=entity.coin_reward,
        is_active=entity.is_active,
    )


def _completion_to_domain(model: MissionCompletionModel) -> MissionCompletion:
    return MissionCompletion(
        user_id=model.user_id,
        mission_id=model.mission_id,
        id=model.id,
        completed_at=model.completed_at,
    )


def _completion_to_model(entity: MissionCompletion) -> MissionCompletionModel:
    return MissionCompletionModel(
        id=entity.id,
        user_id=entity.user_id,
        mission_id=entity.mission_id,
        completed_at=entity.completed_at,
    )


class PostgresMissionRepository(MissionRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, mission_id: UUID) -> Mission | None:
        stmt = select(MissionModel).where(MissionModel.id == mission_id)
        model = self._session.execute(statement=stmt).scalar_one_or_none()
        if model is None:
            return None
        return _mission_to_domain(model=model)

    def get_all_active(self) -> list[Mission]:
        stmt = select(MissionModel).where(MissionModel.is_active.is_(True))
        models = self._session.execute(statement=stmt).scalars().all()
        return [_mission_to_domain(model=m) for m in models]

    def save(self, mission: Mission) -> Mission:
        self._session.add(instance=_mission_to_model(entity=mission))
        self._session.flush()
        return mission

    def save_completion(self, completion: MissionCompletion) -> MissionCompletion:
        self._session.add(instance=_completion_to_model(entity=completion))
        try:
            self._session.flush()
        except IntegrityError as exc:
            raise MissionAlreadyCompletedError(
                user_id=completion.user_id, mission_id=completion.mission_id
            ) from exc
        return completion

    def get_completions_by_user(self, user_id: UUID) -> list[MissionCompletion]:
        stmt = select(MissionCompletionModel).where(MissionCompletionModel.user_id == user_id)
        models = self._session.execute(statement=stmt).scalars().all()
        return [_completion_to_domain(model=m) for m in models]
