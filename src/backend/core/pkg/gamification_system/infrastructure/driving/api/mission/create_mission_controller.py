import logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from core.pkg.gamification_system.domain.entities.mission import Mission
from core.pkg.gamification_system.domain.ports.driving.mission_use_cases import MissionUseCases
from core.pkg.gamification_system.infrastructure.driving.dtos.mission_dtos import CreateMissionRequest, MissionResponse

logger = logging.getLogger(__name__)

class CreateMissionController:

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
        @self.app.post(path=f"{self.base_path}/missions")
        def handle_create_mission(body: CreateMissionRequest) -> JSONResponse:
            try:
                mission = self.use_case.create_mission(
                    title=body.title,
                    description=body.description,
                    xp_reward=body.xp_reward,
                    coin_reward=body.coin_reward,
                )
                response_data = build_response(mission=mission).model_dump(mode="json")
                return JSONResponse(status_code=201, content=response_data)
            except Exception as e:
                logger.error(f"Error creating mission: {e}")
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
