from collections.abc import Callable

import structlog
from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse

from core.pkg.mission_system.domain.entities.mission import Mission
from core.pkg.mission_system.domain.ports.driving.mission_use_cases import MissionUseCases
from core.pkg.mission_system.infrastructure.driving.dtos.mission_dtos import MissionResponse

logger = structlog.get_logger(__name__)


class ListActiveMissionsController:

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
        @self.app.get(path=f"{self.base_path}/missions")
        def handle_list_active_missions(
            use_case: MissionUseCases = Depends(dependency=self.use_case_factory),
        ) -> JSONResponse:
            logger.info("incoming_list_active_missions_request")
            try:
                missions = use_case.list_active_missions()
                response_data = [
                    build_response(mission=m).model_dump(mode="json")
                    for m in missions
                ]
                logger.info(
                    "outgoing_list_active_missions_response",
                    status_code=200,
                    count=len(response_data),
                )
                return JSONResponse(status_code=200, content=response_data)
            except Exception as e:
                logger.error(
                    "list_active_missions_unhandled_error",
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
