from __future__ import annotations

from uuid import UUID

from core.pkg.shared.domain.exceptions.entity_not_found import EntityNotFoundError
from core.pkg.user_system.domain.entities.user import User
from core.pkg.user_system.domain.ports.driven.user_repository import UserRepository
from core.pkg.user_system.domain.ports.driving.user_use_cases import UserUseCases


class UserService(UserUseCases):
    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repo = user_repository

    def get_user(self, user_id: UUID) -> User:
        user = self._user_repo.get_by_id(user_id=user_id)
        if user is None:
            raise EntityNotFoundError(entity_type="User", entity_id=user_id)
        return user

    def list_users(self) -> list[User]:
        return self._user_repo.get_all()

    def create_user(self, username: str, email: str) -> User:
        user = User(username=username, email=email)
        return self._user_repo.save(user=user)
