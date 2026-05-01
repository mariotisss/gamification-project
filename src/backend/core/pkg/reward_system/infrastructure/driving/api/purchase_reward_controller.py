import logging
from uuid import UUID
from fastapi import FastAPI
from fastapi.responses import JSONResponse

from core.pkg.reward_system.domain.entities.reward import Reward
from core.pkg.reward_system.domain.exceptions.insufficient_coins import InsufficientCoinsError
from core.pkg.reward_system.domain.ports.driving.reward_use_cases import RewardUseCases
from core.pkg.reward_system.infrastructure.driving.dtos.reward_dtos import PurchaseRewardRequest, RewardResponse
from core.pkg.shared.domain.exceptions.entity_not_found import EntityNotFoundError

logger = logging.getLogger(__name__)

class PurchaseRewardController:

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
        @self.app.post(path=f"{self.base_path}/rewards/{{reward_id}}/purchase")
        def handle_purchase_reward(reward_id: UUID, body: PurchaseRewardRequest) -> JSONResponse:
            try:
                reward = self.use_case.purchase_reward(
                    user_id=body.user_id,
                    reward_id=reward_id,
                )
                response_data = build_response(reward=reward).model_dump(mode="json")
                return JSONResponse(status_code=200, content=response_data)
            except EntityNotFoundError as e:
                return JSONResponse(status_code=404, content={"detail": str(e)})
            except InsufficientCoinsError as e:
                return JSONResponse(status_code=402, content={"detail": str(e)})
            except Exception as e:
                logger.error(f"Error purchasing reward: {e}")
                return JSONResponse(status_code=500, content={"detail": "Internal server error"})

        def build_response(reward: Reward) -> RewardResponse:
            return RewardResponse(
                id=str(reward.id),
                name=reward.name,
                description=reward.description,
                cost=reward.cost,
                reward_type=reward.reward_type,
            )
