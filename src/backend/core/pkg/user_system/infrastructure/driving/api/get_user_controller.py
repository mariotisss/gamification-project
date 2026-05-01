import logging
from uuid import UUID
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from core.pkg.shared.domain.exceptions.entity_not_found import EntityNotFoundError
from core.pkg.user_system.domain.entities.user import User
from core.pkg.user_system.domain.ports.driving.user_use_cases import UserUseCases
from core.pkg.user_system.infrastructure.driving.dtos.user_dtos import UserResponse

logger = logging.getLogger(__name__)

class GetUserController:

    def __init__(
        self,
        app: FastAPI,
        use_case: UserUseCases,
        base_path: str,
    ) -> None:
        self.app = app
        self.use_case = use_case
        self.base_path = base_path

    def register_routes(self) -> None:

        @self.app.get(path=f"{self.base_path}/users/{{user_id}}")
        def handle_get_user(user_id: UUID) -> JSONResponse:
            try:
                user = self.use_case.get_user(user_id=user_id)
                response_data = build_response(user=user).model_dump(mode="json")
                return JSONResponse(status_code=200, content=response_data)
            except EntityNotFoundError as e:
                return JSONResponse(status_code=404, content={"detail": str(e)})
            except Exception as e:
                logger.error(f"Error getting user: {e}")
                return JSONResponse(status_code=500, content={"detail": "Internal server error"})

        def build_response(user: User) -> UserResponse:
            return UserResponse(
                id=str(user.id),
                username=user.username,
                email=user.email,
                xp=user.xp,
                level=user.level,
                dev_coins=user.dev_coins,
                created_at=user.created_at.isoformat(),
            )
