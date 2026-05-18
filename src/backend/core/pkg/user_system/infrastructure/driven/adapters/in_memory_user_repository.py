from __future__ import annotations

from uuid import UUID

from core.pkg.shared.domain.exceptions.entity_not_found import EntityNotFoundError
from core.pkg.user_system.domain.entities.user import User
from core.pkg.user_system.domain.ports.driven.user_repository import UserRepository


class InMemoryUserRepository(UserRepository):
    def __init__(self) -> None:
        self._storage: dict[UUID, User] = {}

    def get_by_id(self, user_id: UUID) -> User:
        user = self._storage.get(user_id)
        if user is None:
            raise EntityNotFoundError(entity_type="User", entity_id=user_id)
        return user

    def get_all(self) -> list[User]:
        return list(self._storage.values())

    def save(self, user: User) -> User:
        self._storage[user.id] = user
        return user

    def update(self, user: User) -> User:
        self._storage[user.id] = user
        return user
