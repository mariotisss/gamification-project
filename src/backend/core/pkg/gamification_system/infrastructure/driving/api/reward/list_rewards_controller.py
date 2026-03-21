import logging
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from core.pkg.gamification_system.domain.entities.reward import Reward
from core.pkg.gamification_system.domain.ports.driving.reward_use_cases import RewardUseCases
from core.pkg.gamification_system.infrastructure.driving.dtos.reward_dtos import RewardResponse

logger = logging.getLogger(__name__)

class ListRewardsController:

    def __init__(
        self,
        app: FastAPI,
        use_case: RewardUseCases,
        base_path: str,
    ) -> None:
        self.app = app
        self.use_case = use_case
        self.base_path = base_path

    def register_routes(self) -> None:
        @self.app.get(path=f"{self.base_path}/rewards")
        def handle_list_rewards() -> JSONResponse:
            try:
                rewards = self.use_case.list_rewards()
                response_data = [
                    build_response(reward=r).model_dump(mode="json")
                    for r in rewards
                ]
                return JSONResponse(status_code=200, content=response_data)
            except Exception as e:
                logger.error(f"Error listing rewards: {e}")
                return JSONResponse(status_code=500, content={"detail": "Internal server error"})

        def build_response(reward: Reward) -> RewardResponse:
            return RewardResponse(
                id=str(reward.id),
                name=reward.name,
                description=reward.description,
                cost=reward.cost,
                reward_type=reward.reward_type,
            )
