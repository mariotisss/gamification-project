import logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from core.pkg.user_system.domain.entities.user import User
from core.pkg.user_system.domain.ports.driving.user_use_cases import UserUseCases
from core.pkg.user_system.infrastructure.driving.dtos.user_dtos import CreateUserRequest, UserResponse

logger = logging.getLogger(__name__)

class CreateUserController:

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
        @self.app.post(path=f"{self.base_path}/users")
        def handle_create_user(body: CreateUserRequest) -> JSONResponse:
            try:
                user = self.use_case.create_user(username=body.username, email=body.email)
                response_data = build_response(user=user).model_dump(mode="json")
                return JSONResponse(status_code=201, content=response_data)
            except Exception as e:
                logger.error(f"Error creating user: {e}")
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
