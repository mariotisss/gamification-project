import logging
from uuid import UUID
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from core.pkg.gamification_system.domain.exceptions.entity_not_found import EntityNotFoundError
from core.pkg.gamification_system.domain.exceptions.mission_already_completed import MissionAlreadyCompletedError
from core.pkg.gamification_system.domain.ports.driving.mission_use_cases import MissionUseCases
from core.pkg.gamification_system.infrastructure.driving.dtos.mission_dtos import CompleteMissionRequest, MissionCompletionResponse

logger = logging.getLogger(__name__)

class CompleteMissionController:

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
        @self.app.post(path=f"{self.base_path}/missions/{{mission_id}}/complete")
        def handle_complete_mission(mission_id: UUID, body: CompleteMissionRequest) -> JSONResponse:
            try:
                completion = self.use_case.complete_mission(
                    user_id=body.user_id,
                    mission_id=mission_id,
                )
                response_data = MissionCompletionResponse(
                    id=str(completion.id),
                    user_id=str(completion.user_id),
                    mission_id=str(completion.mission_id),
                    completed_at=completion.completed_at.isoformat(),
                ).model_dump(mode="json")
                return JSONResponse(status_code=201, content=response_data)
            except EntityNotFoundError as e:
                return JSONResponse(status_code=404, content={"detail": str(e)})
            except MissionAlreadyCompletedError as e:
                return JSONResponse(status_code=409, content={"detail": str(e)})
            except Exception as e:
                logger.error(f"Error completing mission: {e}")
                return JSONResponse(status_code=500, content={"detail": "Internal server error"})
