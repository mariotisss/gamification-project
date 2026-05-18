from collections.abc import Callable
from uuid import UUID

import structlog
from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse

from core.pkg.shared.domain.exceptions.entity_not_found import EntityNotFoundError
from core.pkg.user_system.domain.entities.user import User
from core.pkg.user_system.domain.ports.driving.user_use_cases import UserUseCases
from core.pkg.user_system.infrastructure.driving.dtos.user_dtos import UserResponse

logger = structlog.get_logger(__name__)


class GetUserController:

    def __init__(
        self,
        app: FastAPI,
        use_case_factory: Callable[..., UserUseCases],
        base_path: str,
    ) -> None:
        self.app = app
        self.use_case_factory = use_case_factory
        self.base_path = base_path

    def register_routes(self) -> None:
        @self.app.get(path=f"{self.base_path}/users/{{user_id}}")
        def handle_get_user(
            user_id: UUID,
            use_case: UserUseCases = Depends(dependency=self.use_case_factory),
        ) -> JSONResponse:
            logger.info("incoming_get_user_request", user_id=str(user_id))
            try:
                user = use_case.get_user(user_id=user_id)
                response_data = build_response(user=user).model_dump(mode="json")
                logger.info(
                    "outgoing_get_user_response",
                    status_code=200,
                    user_id=str(user_id),
                )
                return JSONResponse(status_code=200, content=response_data)
            except EntityNotFoundError as e:
                logger.error(
                    "get_user_not_found",
                    user_id=str(user_id),
                    exc_type=type(e).__name__,
                    message=str(e),
                )
                return JSONResponse(status_code=404, content={"detail": str(e)})
            except Exception as e:
                logger.error(
                    "get_user_unhandled_error",
                    user_id=str(user_id),
                    exc_type=type(e).__name__,
                    message=str(e),
                    exc_info=True,
                )
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
