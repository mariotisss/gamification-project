import logging
from collections.abc import Callable
from uuid import UUID

from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse

from core.pkg.mission_system.domain.entities.mission import Mission
from core.pkg.mission_system.domain.ports.driving.mission_use_cases import MissionUseCases
from core.pkg.mission_system.infrastructure.driving.dtos.mission_dtos import MissionResponse
from core.pkg.shared.domain.exceptions.entity_not_found import EntityNotFoundError

logger = logging.getLogger(__name__)


class GetMissionController:

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
        @self.app.get(path=f"{self.base_path}/missions/{{mission_id}}")
        def handle_get_mission(
            mission_id: UUID,
            use_case: MissionUseCases = Depends(dependency=self.use_case_factory),
        ) -> JSONResponse:
            try:
                mission = use_case.get_mission(mission_id=mission_id)
                response_data = build_response(mission=mission).model_dump(mode="json")
                return JSONResponse(status_code=200, content=response_data)
            except EntityNotFoundError as e:
                return JSONResponse(status_code=404, content={"detail": str(e)})
            except Exception as e:
                logger.error(f"Error getting mission: {e}")
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
