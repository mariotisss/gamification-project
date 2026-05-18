from collections.abc import Callable

import structlog
from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse

from core.pkg.reward_system.domain.entities.reward import Reward
from core.pkg.reward_system.domain.ports.driving.reward_use_cases import RewardUseCases
from core.pkg.reward_system.infrastructure.driving.dtos.reward_dtos import RewardResponse

logger = structlog.get_logger(__name__)


class ListRewardsController:

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
        @self.app.get(path=f"{self.base_path}/rewards")
        def handle_list_rewards(
            use_case: RewardUseCases = Depends(dependency=self.use_case_factory),
        ) -> JSONResponse:
            logger.info("incoming_list_rewards_request")
            try:
                rewards = use_case.list_rewards()
                response_data = [
                    build_response(reward=r).model_dump(mode="json")
                    for r in rewards
                ]
                logger.info(
                    "outgoing_list_rewards_response",
                    status_code=200,
                    count=len(response_data),
                )
                return JSONResponse(status_code=200, content=response_data)
            except Exception as e:
                logger.error(
                    "list_rewards_unhandled_error",
                    exc_type=type(e).__name__,
                    message=str(e),
                    exc_info=True,
                )
                return JSONResponse(status_code=500, content={"detail": "Internal server error"})

        def build_response(reward: Reward) -> RewardResponse:
            return RewardResponse(
                id=str(reward.id),
                name=reward.name,
                description=reward.description,
                cost=reward.cost,
                reward_type=reward.reward_type,
            )
