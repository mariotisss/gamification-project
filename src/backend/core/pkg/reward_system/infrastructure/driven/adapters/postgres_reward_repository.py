from __future__ import annotations

from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.pkg.reward_system.domain.entities.reward import Reward
from core.pkg.reward_system.domain.ports.driven.reward_repository import RewardRepository
from core.pkg.reward_system.infrastructure.driven.persistence.models.reward_model import (
    RewardModel,
)
from core.pkg.shared.domain.exceptions.entity_not_found import EntityNotFoundError

logger = structlog.get_logger(__name__)


def _to_domain(model: RewardModel) -> Reward:
    return Reward(
        name=model.name,
        description=model.description,
        cost=model.cost,
        reward_type=model.reward_type,
        id=model.id,
    )


def _to_model(entity: Reward) -> RewardModel:
    return RewardModel(
        id=entity.id,
        name=entity.name,
        description=entity.description,
        cost=entity.cost,
        reward_type=entity.reward_type,
    )


class PostgresRewardRepository(RewardRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, reward_id: UUID) -> Reward:
        logger.info(
            "repo_get_by_id_called",
            repo="PostgresRewardRepository",
            reward_id=str(reward_id),
        )
        stmt = select(RewardModel).where(RewardModel.id == reward_id)
        model = self._session.execute(statement=stmt).scalar_one_or_none()
        if model is None:
            logger.error(
                "repo_entity_not_found",
                repo="PostgresRewardRepository",
                op="get_by_id",
                reward_id=str(reward_id),
            )
            raise EntityNotFoundError(entity_type="Reward", entity_id=reward_id)
        logger.info(
            "repo_get_by_id_returned",
            repo="PostgresRewardRepository",
            reward_id=str(reward_id),
        )
        return _to_domain(model=model)

    def get_all(self) -> list[Reward]:
        logger.info("repo_get_all_called", repo="PostgresRewardRepository")
        stmt = select(RewardModel).order_by(RewardModel.cost)
        models = self._session.execute(statement=stmt).scalars().all()
        rewards = [_to_domain(model=m) for m in models]
        logger.info(
            "repo_get_all_returned",
            repo="PostgresRewardRepository",
            count=len(rewards),
        )
        return rewards

    def save(self, reward: Reward) -> Reward:
        logger.info(
            "repo_save_called",
            repo="PostgresRewardRepository",
            reward_id=str(reward.id),
        )
        self._session.add(instance=_to_model(entity=reward))
        self._session.flush()
        logger.info(
            "repo_save_returned",
            repo="PostgresRewardRepository",
            reward_id=str(reward.id),
        )
        return reward
