from fastapi import FastAPI
import uvicorn

# ── Driven adapters (outbound) ───────────────────────────────────
from core.pkg.gamification_system.infrastructure.driven.adapters.in_memory_user_repository import InMemoryUserRepository
from core.pkg.gamification_system.infrastructure.driven.adapters.in_memory_mission_repository import InMemoryMissionRepository
from core.pkg.gamification_system.infrastructure.driven.adapters.in_memory_reward_repository import InMemoryRewardRepository

# ── Application services ─────────────────────────────────────────
from core.pkg.gamification_system.application.use_cases.user_service import UserService
from core.pkg.gamification_system.application.use_cases.mission_service import MissionService
from core.pkg.gamification_system.application.use_cases.reward_service import RewardService

# ── Driving adapters (inbound) ───────────────────────────────────
from core.pkg.gamification_system.infrastructure.driving.api.user.list_users_controller import ListUsersController
from core.pkg.gamification_system.infrastructure.driving.api.user.get_user_controller import GetUserController
from core.pkg.gamification_system.infrastructure.driving.api.user.create_user_controller import CreateUserController

from core.pkg.gamification_system.infrastructure.driving.api.mission.list_active_missions_controller import ListActiveMissionsController
from core.pkg.gamification_system.infrastructure.driving.api.mission.get_mission_controller import GetMissionController
from core.pkg.gamification_system.infrastructure.driving.api.mission.create_mission_controller import CreateMissionController
from core.pkg.gamification_system.infrastructure.driving.api.mission.complete_mission_controller import CompleteMissionController

from core.pkg.gamification_system.infrastructure.driving.api.reward.list_rewards_controller import ListRewardsController
from core.pkg.gamification_system.infrastructure.driving.api.reward.get_reward_controller import GetRewardController
from core.pkg.gamification_system.infrastructure.driving.api.reward.create_reward_controller import CreateRewardController
from core.pkg.gamification_system.infrastructure.driving.api.reward.purchase_reward_controller import PurchaseRewardController

from core.pkg.gamification_system.infrastructure.driving.api.health.health_check_controller import HealthCheckController

# ─────────────────────────────────────────────────────────────────
# 1. Instantiate repositories (in-memory for now)
# ─────────────────────────────────────────────────────────────────
user_repo = InMemoryUserRepository()
mission_repo = InMemoryMissionRepository()
reward_repo = InMemoryRewardRepository()

# ─────────────────────────────────────────────────────────────────
# 2. Wire services (application layer)
# ─────────────────────────────────────────────────────────────────
user_service = UserService(user_repository=user_repo)
mission_service = MissionService(mission_repository=mission_repo, user_repository=user_repo)
reward_service = RewardService(reward_repository=reward_repo, user_repository=user_repo)

# ─────────────────────────────────────────────────────────────────
# 3. Create the FastAPI application
# ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Gamification API",
    description="Developer productivity gamification platform — Phase 1",
    version="0.1.0",
)

# ─────────────────────────────────────────────────────────────────
# 4. Inject services into controllers and register routes
# ─────────────────────────────────────────────────────────────────
ListUsersController(app=app, use_case=user_service, base_path="/api").register_routes()
GetUserController(app=app, use_case=user_service, base_path="/api").register_routes()
CreateUserController(app=app, use_case=user_service, base_path="/api").register_routes()

ListActiveMissionsController(app=app, use_case=mission_service, base_path="/api").register_routes()
GetMissionController(app=app, use_case=mission_service, base_path="/api").register_routes()
CreateMissionController(app=app, use_case=mission_service, base_path="/api").register_routes()
CompleteMissionController(app=app, use_case=mission_service, base_path="/api").register_routes()

ListRewardsController(app=app, use_case=reward_service, base_path="/api").register_routes()
GetRewardController(app=app, use_case=reward_service, base_path="/api").register_routes()
CreateRewardController(app=app, use_case=reward_service, base_path="/api").register_routes()
PurchaseRewardController(app=app, use_case=reward_service, base_path="/api").register_routes()

HealthCheckController(app=app, base_path="/api").register_routes()


if __name__ == "__main__":

    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)