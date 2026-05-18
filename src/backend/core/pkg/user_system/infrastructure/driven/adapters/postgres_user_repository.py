from __future__ import annotations

from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError

from core.pkg.shared.domain.exceptions.entity_not_found import EntityNotFoundError
from core.pkg.user_system.domain.entities.user import User
from core.pkg.user_system.domain.exceptions.concurrent_user_update import (
    ConcurrentUserUpdateError,
)
from core.pkg.user_system.domain.exceptions.user_already_exists import UserAlreadyExistsError
from core.pkg.user_system.domain.ports.driven.user_repository import UserRepository
from core.pkg.user_system.infrastructure.driven.persistence.models.user_model import UserModel

logger = structlog.get_logger(__name__)


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

    def get_by_id(self, user_id: UUID) -> User:
        logger.info(
            "repo_get_by_id_called",
            repo="PostgresUserRepository",
            user_id=str(user_id),
        )
        stmt = select(UserModel).where(UserModel.id == user_id)
        model = self._session.execute(statement=stmt).scalar_one_or_none()
        if model is None:
            logger.error(
                "repo_entity_not_found",
                repo="PostgresUserRepository",
                op="get_by_id",
                user_id=str(user_id),
            )
            raise EntityNotFoundError(entity_type="User", entity_id=user_id)
        logger.info(
            "repo_get_by_id_returned",
            repo="PostgresUserRepository",
            user_id=str(user_id),
        )
        return _to_domain(model=model)

    def get_all(self) -> list[User]:
        logger.info("repo_get_all_called", repo="PostgresUserRepository")
        stmt = select(UserModel).order_by(UserModel.created_at)
        models = self._session.execute(statement=stmt).scalars().all()
        users = [_to_domain(model=m) for m in models]
        logger.info(
            "repo_get_all_returned",
            repo="PostgresUserRepository",
            count=len(users),
        )
        return users

    def save(self, user: User) -> User:
        logger.info(
            "repo_save_called",
            repo="PostgresUserRepository",
            user_id=str(user.id),
        )
        model = _to_model(entity=user)
        self._session.add(instance=model)
        try:
            self._session.flush()
        except IntegrityError as exc:
            logger.error(
                "repo_user_already_exists",
                repo="PostgresUserRepository",
                op="save",
                username=user.username,
                email=user.email,
            )
            raise UserAlreadyExistsError(username=user.username, email=user.email) from exc
        logger.info(
            "repo_save_returned",
            repo="PostgresUserRepository",
            user_id=str(user.id),
        )
        return user

    def update(self, user: User) -> User:
        logger.info(
            "repo_update_called",
            repo="PostgresUserRepository",
            user_id=str(user.id),
        )
        stmt = select(UserModel).where(UserModel.id == user.id)
        model = self._session.execute(statement=stmt).scalar_one()
        model.username = user.username
        model.email = user.email
        model.xp = user.xp
        model.level = user.level
        model.dev_coins = user.dev_coins
        try:
            self._session.flush()
        except StaleDataError as exc:
            logger.error(
                "repo_concurrent_user_update",
                repo="PostgresUserRepository",
                op="update",
                user_id=str(user.id),
            )
            raise ConcurrentUserUpdateError(user_id=user.id) from exc
        logger.info(
            "repo_update_returned",
            repo="PostgresUserRepository",
            user_id=str(user.id),
        )
        return user
