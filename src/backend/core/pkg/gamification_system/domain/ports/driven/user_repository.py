from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from core.pkg.gamification_system.domain.entities.user import User


class UserRepository(ABC):
    @abstractmethod
    def get_by_id(self, user_id: UUID) -> User | None:
        pass

    @abstractmethod
    def get_all(self) -> list[User]:
        pass

    @abstractmethod
    def save(self, user: User) -> User:
        pass

    @abstractmethod
    def update(self, user: User) -> User:
        pass
