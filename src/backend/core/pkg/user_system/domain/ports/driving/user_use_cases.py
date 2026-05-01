from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import UUID

from core.pkg.user_system.domain.entities.user import User


class UserUseCases(ABC):
    @abstractmethod
    def get_user(self, user_id: UUID) -> User:
        pass

    @abstractmethod
    def list_users(self) -> list[User]:
        pass

    @abstractmethod
    def create_user(self, username: str, email: str) -> User:
        pass
