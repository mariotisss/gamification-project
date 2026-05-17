from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.pkg.user_system.domain.entities.user import User
from core.pkg.user_system.domain.ports.driven.user_repository import UserRepository
from core.pkg.user_system.infrastructure.driven.persistence.models.user_model import UserModel


def _to_domain(model: UserModel) -> User:
    return User(
        username=model.username,
        email=model.email,
        id=model.id,
        xp=model.xp,
        level=model.level,
        dev_coins=model.dev_coins,
        created_at=model.created_at,
    )


def _to_model(entity: User) -> UserModel:
    return UserModel(
        id=entity.id,
        username=entity.username,
        email=entity.email,
        xp=entity.xp,
        level=entity.level,
        dev_coins=entity.dev_coins,
        created_at=entity.created_at,
    )


class PostgresUserRepository(UserRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, user_id: UUID) -> User | None:
        stmt = select(UserModel).where(UserModel.id == user_id)
        model = self._session.execute(statement=stmt).scalar_one_or_none()
        if model is None:
            return None
        return _to_domain(model=model)

    def get_all(self) -> list[User]:
        stmt = select(UserModel).order_by(UserModel.created_at)
        models = self._session.execute(statement=stmt).scalars().all()
        return [_to_domain(model=m) for m in models]

    def save(self, user: User) -> User:
        model = _to_model(entity=user)
        self._session.add(instance=model)
        self._session.flush()
        return user

    def update(self, user: User) -> User:
        stmt = select(UserModel).where(UserModel.id == user.id)
        model = self._session.execute(statement=stmt).scalar_one()
        model.username = user.username
        model.email = user.email
        model.xp = user.xp
        model.level = user.level
        model.dev_coins = user.dev_coins
        self._session.flush()
        return user
