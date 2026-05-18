from collections.abc import Callable

import structlog
from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse

from core.pkg.mission_system.domain.entities.mission import Mission
from core.pkg.mission_system.domain.ports.driving.mission_use_cases import MissionUseCases
from core.pkg.mission_system.infrastructure.driving.dtos.mission_dtos import (
    CreateMissionRequest,
    MissionResponse,
)

logger = structlog.get_logger(__name__)


class CreateMissionController:

    def __init__(
        self,
        app: FastAPI,
        use_case_factory: Callable[..., MissionUseCases],
        base_path: str,
    ) -> None:
        self.app = app
        self.use_case_factory = use_case_factory
        self.base_path = base_path

    def register_routes(self) -> None:
        @self.app.post(path=f"{self.base_path}/missions")
        def handle_create_mission(
            body: CreateMissionRequest,
            use_case: MissionUseCases = Depends(dependency=self.use_case_factory),
        ) -> JSONResponse:
            logger.info(
                "incoming_create_mission_request",
                title=body.title,
                xp_reward=body.xp_reward,
                coin_reward=body.coin_reward,
            )
            try:
                mission = use_case.create_mission(
                    title=body.title,
                    description=body.description,
                    xp_reward=body.xp_reward,
                    coin_reward=body.coin_reward,
                )
                response_data = build_response(mission=mission).model_dump(mode="json")
                logger.info(
                    "outgoing_create_mission_response",
                    status_code=201,
                    mission_id=str(mission.id),
                )
                return JSONResponse(status_code=201, content=response_data)
            except Exception as e:
                logger.error(
                    "create_mission_unhandled_error",
                    exc_type=type(e).__name__,
                    message=str(e),
                    exc_info=True,
                )
                return JSONResponse(status_code=500, content={"detail": "Internal server error"})

        def build_response(mission: Mission) -> MissionResponse:
            return MissionResponse(
                id=str(mission.id),
                title=mission.title,
                description=mission.description,
                xp_reward=mission.xp_reward,
                coin_reward=mission.coin_reward,
                is_active=mission.is_active,
            )
