import logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from core.pkg.mission_system.domain.entities.mission import Mission
from core.pkg.mission_system.domain.ports.driving.mission_use_cases import MissionUseCases
from core.pkg.mission_system.infrastructure.driving.dtos.mission_dtos import MissionResponse

logger = logging.getLogger(__name__)

class ListActiveMissionsController:

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
        @self.app.get(path=f"{self.base_path}/missions")
        def handle_list_active_missions() -> JSONResponse:
            try:
                missions = self.use_case.list_active_missions()
                response_data = [
                    build_response(mission=m).model_dump(mode="json")
                    for m in missions
                ]
                return JSONResponse(status_code=200, content=response_data)
            except Exception as e:
                logger.error(f"Error listing active missions: {e}")
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
