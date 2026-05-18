from collections.abc import Callable
from uuid import UUID

import structlog
from fastapi import Depends, FastAPI
from fastapi.responses import JSONResponse

from core.pkg.reward_system.domain.entities.reward import Reward
from core.pkg.reward_system.domain.exceptions.insufficient_coins import InsufficientCoinsError
from core.pkg.reward_system.domain.ports.driving.reward_use_cases import RewardUseCases
from core.pkg.reward_system.infrastructure.driving.dtos.reward_dtos import (
    PurchaseRewardRequest,
    RewardResponse,
)
from core.pkg.shared.domain.exceptions.entity_not_found import EntityNotFoundError
from core.pkg.user_system.domain.exceptions.concurrent_user_update import (
    ConcurrentUserUpdateError,
)

logger = structlog.get_logger(__name__)


class PurchaseRewardController:

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
        @self.app.post(path=f"{self.base_path}/rewards/{{reward_id}}/purchase")
        def handle_purchase_reward(
            reward_id: UUID,
            body: PurchaseRewardRequest,
            use_case: RewardUseCases = Depends(dependency=self.use_case_factory),
        ) -> JSONResponse:
            logger.info(
                "incoming_purchase_reward_request",
                user_id=str(body.user_id),
                reward_id=str(reward_id),
            )
            try:
                reward = use_case.purchase_reward(
                    user_id=body.user_id,
                    reward_id=reward_id,
                )
                response_data = build_response(reward=reward).model_dump(mode="json")
                logger.info(
                    "outgoing_purchase_reward_response",
                    status_code=200,
                    reward_id=str(reward_id),
                )
                return JSONResponse(status_code=200, content=response_data)
            except EntityNotFoundError as e:
                logger.error(
                    "purchase_reward_not_found",
                    user_id=str(body.user_id),
                    reward_id=str(reward_id),
                    exc_type=type(e).__name__,
                    message=str(e),
                )
                return JSONResponse(status_code=404, content={"detail": str(e)})
            except InsufficientCoinsError as e:
                logger.error(
                    "purchase_reward_insufficient_coins",
                    user_id=str(body.user_id),
                    reward_id=str(reward_id),
                    exc_type=type(e).__name__,
                    message=str(e),
                )
                return JSONResponse(status_code=402, content={"detail": str(e)})
            except ConcurrentUserUpdateError as e:
                logger.error(
                    "purchase_reward_concurrent_user_update",
                    user_id=str(body.user_id),
                    reward_id=str(reward_id),
                    exc_type=type(e).__name__,
                    message=str(e),
                )
                return JSONResponse(status_code=409, content={"detail": str(e)})
            except Exception as e:
                logger.error(
                    "purchase_reward_unhandled_error",
                    user_id=str(body.user_id),
                    reward_id=str(reward_id),
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
