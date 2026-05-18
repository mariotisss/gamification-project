from collections.abc import Callable

import structlog
from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse

from core.pkg.user_system.domain.entities.user import User
from core.pkg.user_system.domain.exceptions.user_already_exists import UserAlreadyExistsError
from core.pkg.user_system.domain.ports.driving.user_use_cases import UserUseCases
from core.pkg.user_system.infrastructure.driving.dtos.user_dtos import (
    CreateUserRequest,
    UserResponse,
)

logger = structlog.get_logger(__name__)


class CreateUserController:

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
        @self.app.post(path=f"{self.base_path}/users")
        def handle_create_user(
            body: CreateUserRequest,
            use_case: UserUseCases = Depends(dependency=self.use_case_factory),
        ) -> JSONResponse:
            logger.info(
                "incoming_create_user_request",
                username=body.username,
                email=body.email,
            )
            try:
                user = use_case.create_user(username=body.username, email=body.email)
                response_data = build_response(user=user).model_dump(mode="json")
                logger.info(
                    "outgoing_create_user_response",
                    status_code=201,
                    user_id=str(user.id),
                )
                return JSONResponse(status_code=201, content=response_data)
            except UserAlreadyExistsError as e:
                logger.error(
                    "create_user_already_exists",
                    username=body.username,
                    email=body.email,
                    exc_type=type(e).__name__,
                    message=str(e),
                )
                return JSONResponse(status_code=409, content={"detail": str(e)})
            except Exception as e:
                logger.error(
                    "create_user_unhandled_error",
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
