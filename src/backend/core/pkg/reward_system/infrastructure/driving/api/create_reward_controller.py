import logging
from collections.abc import Callable

from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse

from core.pkg.reward_system.domain.entities.reward import Reward
from core.pkg.reward_system.domain.ports.driving.reward_use_cases import RewardUseCases
from core.pkg.reward_system.infrastructure.driving.dtos.reward_dtos import (
    CreateRewardRequest,
    RewardResponse,
)

logger = logging.getLogger(__name__)


class CreateRewardController:

    def __init__(
        self,
        app: FastAPI,
        use_case_factory: Callable[..., RewardUseCases],
        base_path: str,
    ) -> None:
        self.app = app
        self.use_case_factory = use_case_factory
        self.base_path = base_path

    def register_routes(self) -> None:
        @self.app.post(path=f"{self.base_path}/rewards")
        def handle_create_reward(
            body: CreateRewardRequest,
            use_case: RewardUseCases = Depends(dependency=self.use_case_factory),
        ) -> JSONResponse:
            try:
                reward = use_case.create_reward(
                    name=body.name,
                    description=body.description,
                    cost=body.cost,
                    reward_type=body.reward_type,
                )
                response_data = build_response(reward=reward).model_dump(mode="json")
                return JSONResponse(status_code=201, content=response_data)
            except Exception as e:
                logger.error(f"Error creating reward: {e}")
                return JSONResponse(status_code=500, content={"detail": "Internal server error"})

        def build_response(reward: Reward) -> RewardResponse:
            return RewardResponse(
                id=str(reward.id),
                name=reward.name,
                description=reward.description,
                cost=reward.cost,
                reward_type=reward.reward_type,
            )
