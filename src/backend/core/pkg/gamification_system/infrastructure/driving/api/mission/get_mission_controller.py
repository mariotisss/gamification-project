import logging
from uuid import UUID
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from core.pkg.gamification_system.domain.entities.mission import Mission
from core.pkg.gamification_system.domain.exceptions.entity_not_found import EntityNotFoundError
from core.pkg.gamification_system.domain.ports.driving.mission_use_cases import MissionUseCases
from core.pkg.gamification_system.infrastructure.driving.dtos.mission_dtos import MissionResponse

logger = logging.getLogger(__name__)

class GetMissionController:

    def __init__(
        self,
        app: FastAPI,
        use_case: MissionUseCases,
        base_path: str,
    ) -> None:
        self.app = app
        self.use_case = use_case
        self.base_path = base_path

    def register_routes(self) -> None:
        @self.app.get(path=f"{self.base_path}/missions/{{mission_id}}")
        def handle_get_mission(mission_id: UUID) -> JSONResponse:
            try:
                mission = self.use_case.get_mission(mission_id=mission_id)
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
