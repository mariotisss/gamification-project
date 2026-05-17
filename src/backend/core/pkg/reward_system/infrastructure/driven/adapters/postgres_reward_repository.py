from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.pkg.reward_system.domain.entities.reward import Reward
from core.pkg.reward_system.domain.ports.driven.reward_repository import RewardRepository
from core.pkg.reward_system.infrastructure.driven.persistence.models.reward_model import (
    RewardModel,
)


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

    def get_by_id(self, reward_id: UUID) -> Reward | None:
        stmt = select(RewardModel).where(RewardModel.id == reward_id)
        model = self._session.execute(statement=stmt).scalar_one_or_none()
        if model is None:
            return None
        return _to_domain(model=model)

    def get_all(self) -> list[Reward]:
        stmt = select(RewardModel).order_by(RewardModel.cost)
        models = self._session.execute(statement=stmt).scalars().all()
        return [_to_domain(model=m) for m in models]

    def save(self, reward: Reward) -> Reward:
        self._session.add(instance=_to_model(entity=reward))
        self._session.flush()
        return reward
