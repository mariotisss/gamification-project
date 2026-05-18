from __future__ import annotations

from uuid import UUID

import structlog
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
from core.pkg.shared.domain.exceptions.entity_not_found import EntityNotFoundError

logger = structlog.get_logger(__name__)


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

    def get_by_id(self, mission_id: UUID) -> Mission:
        logger.info(
            "repo_get_by_id_called",
            repo="PostgresMissionRepository",
            mission_id=str(mission_id),
        )
        stmt = select(MissionModel).where(MissionModel.id == mission_id)
        model = self._session.execute(statement=stmt).scalar_one_or_none()
        if model is None:
            logger.error(
                "repo_entity_not_found",
                repo="PostgresMissionRepository",
                op="get_by_id",
                mission_id=str(mission_id),
            )
            raise EntityNotFoundError(entity_type="Mission", entity_id=mission_id)
        logger.info(
            "repo_get_by_id_returned",
            repo="PostgresMissionRepository",
            mission_id=str(mission_id),
        )
        return _mission_to_domain(model=model)

    def get_all_active(self) -> list[Mission]:
        logger.info("repo_get_all_active_called", repo="PostgresMissionRepository")
        stmt = select(MissionModel).where(MissionModel.is_active.is_(True))
        models = self._session.execute(statement=stmt).scalars().all()
        missions = [_mission_to_domain(model=m) for m in models]
        logger.info(
            "repo_get_all_active_returned",
            repo="PostgresMissionRepository",
            count=len(missions),
        )
        return missions

    def save(self, mission: Mission) -> Mission:
        logger.info(
            "repo_save_called",
            repo="PostgresMissionRepository",
            mission_id=str(mission.id),
        )
        self._session.add(instance=_mission_to_model(entity=mission))
        self._session.flush()
        logger.info(
            "repo_save_returned",
            repo="PostgresMissionRepository",
            mission_id=str(mission.id),
        )
        return mission

    def save_completion(self, completion: MissionCompletion) -> MissionCompletion:
        logger.info(
            "repo_save_completion_called",
            repo="PostgresMissionRepository",
            user_id=str(completion.user_id),
            mission_id=str(completion.mission_id),
        )
        self._session.add(instance=_completion_to_model(entity=completion))
        try:
            self._session.flush()
        except IntegrityError as exc:
            logger.error(
                "repo_mission_already_completed",
                repo="PostgresMissionRepository",
                op="save_completion",
                user_id=str(completion.user_id),
                mission_id=str(completion.mission_id),
            )
            raise MissionAlreadyCompletedError(
                user_id=completion.user_id, mission_id=completion.mission_id
            ) from exc
        logger.info(
            "repo_save_completion_returned",
            repo="PostgresMissionRepository",
            completion_id=str(completion.id),
        )
        return completion

    def get_completions_by_user(self, user_id: UUID) -> list[MissionCompletion]:
        logger.info(
            "repo_get_completions_by_user_called",
            repo="PostgresMissionRepository",
            user_id=str(user_id),
        )
        stmt = select(MissionCompletionModel).where(MissionCompletionModel.user_id == user_id)
        models = self._session.execute(statement=stmt).scalars().all()
        completions = [_completion_to_domain(model=m) for m in models]
        logger.info(
            "repo_get_completions_by_user_returned",
            repo="PostgresMissionRepository",
            user_id=str(user_id),
            count=len(completions),
        )
        return completions
