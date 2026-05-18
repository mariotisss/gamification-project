from __future__ import annotations

import uuid
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager

import structlog
import uvicorn
from fastapi import Depends, FastAPI, Request
from sqlalchemy.orm import Session
from starlette.responses import Response

from core.infrastructure.observability.logging import configure_logging
from core.infrastructure.persistence.database import build_engine, build_session_factory
from core.infrastructure.persistence.migration_check import assert_schema_up_to_date
from core.infrastructure.persistence.session_dependency import SessionProvider
from core.infrastructure.persistence.settings import DatabaseSettings

# ── Driven adapters (outbound) ───────────────────────────────────
from core.pkg.user_system.infrastructure.driven.adapters.postgres_user_repository import (
    PostgresUserRepository,
)
from core.pkg.mission_system.infrastructure.driven.adapters.postgres_mission_repository import (
    PostgresMissionRepository,
)
from core.pkg.reward_system.infrastructure.driven.adapters.postgres_reward_repository import (
    PostgresRewardRepository,
)

# ── Application services ─────────────────────────────────────────
from core.pkg.user_system.application.use_cases.user_service import UserService
from core.pkg.mission_system.application.use_cases.mission_service import MissionService
from core.pkg.reward_system.application.use_cases.reward_service import RewardService

# ── Driving adapters (inbound) ───────────────────────────────────
from core.pkg.user_system.infrastructure.driving.api.list_users_controller import (
    ListUsersController,
)
from core.pkg.user_system.infrastructure.driving.api.get_user_controller import GetUserController
from core.pkg.user_system.infrastructure.driving.api.create_user_controller import (
    CreateUserController,
)

from core.pkg.mission_system.infrastructure.driving.api.list_active_missions_controller import (
    ListActiveMissionsController,
)
from core.pkg.mission_system.infrastructure.driving.api.get_mission_controller import (
    GetMissionController,
)
from core.pkg.mission_system.infrastructure.driving.api.create_mission_controller import (
    CreateMissionController,
)
from core.pkg.mission_system.infrastructure.driving.api.complete_mission_controller import (
    CompleteMissionController,
)

from core.pkg.reward_system.infrastructure.driving.api.list_rewards_controller import (
    ListRewardsController,
)
from core.pkg.reward_system.infrastructure.driving.api.get_reward_controller import (
    GetRewardController,
)
from core.pkg.reward_system.infrastructure.driving.api.create_reward_controller import (
    CreateRewardController,
)
from core.pkg.reward_system.infrastructure.driving.api.purchase_reward_controller import (
    PurchaseRewardController,
)

from core.pkg.shared.infrastructure.driving.api.health_check_controller import (
    HealthCheckController,
)


# ─────────────────────────────────────────────────────────────────
# 1. Infrastructure singletons
# ─────────────────────────────────────────────────────────────────
db_settings = DatabaseSettings()
engine = build_engine(settings=db_settings)
session_factory = build_session_factory(engine=engine)
session_provider = SessionProvider(session_factory=session_factory)


# ─────────────────────────────────────────────────────────────────
# 2. Per-request service factories
# ─────────────────────────────────────────────────────────────────
def get_user_service(
    session: Session = Depends(dependency=session_provider.get),
) -> UserService:
    return UserService(user_repository=PostgresUserRepository(session=session))


def get_mission_service(
    session: Session = Depends(dependency=session_provider.get),
) -> MissionService:
    return MissionService(
        mission_repository=PostgresMissionRepository(session=session),
        user_repository=PostgresUserRepository(session=session),
    )


def get_reward_service(
    session: Session = Depends(dependency=session_provider.get),
) -> RewardService:
    return RewardService(
        reward_repository=PostgresRewardRepository(session=session),
        user_repository=PostgresUserRepository(session=session),
    )


# ─────────────────────────────────────────────────────────────────
# 3. Create the FastAPI application
# ─────────────────────────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    assert_schema_up_to_date(engine=engine)
    yield


configure_logging()

app = FastAPI(
    title="Gamification API",
    description="Developer productivity gamification platform — Phase 1",
    version="0.1.0",
    lifespan=lifespan,
)


@app.middleware("http")
async def bind_request_context(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        request_id=str(uuid.uuid4()),
        method=request.method,
        path=request.url.path,
    )
    return await call_next(request)


# ─────────────────────────────────────────────────────────────────
# 4. Register controllers with per-request service factories
# ─────────────────────────────────────────────────────────────────
ListUsersController(
    app=app, use_case_factory=get_user_service, base_path="/api"
).register_routes()
GetUserController(
    app=app, use_case_factory=get_user_service, base_path="/api"
).register_routes()
CreateUserController(
    app=app, use_case_factory=get_user_service, base_path="/api"
).register_routes()

ListActiveMissionsController(
    app=app, use_case_factory=get_mission_service, base_path="/api"
).register_routes()
GetMissionController(
    app=app, use_case_factory=get_mission_service, base_path="/api"
).register_routes()
CreateMissionController(
    app=app, use_case_factory=get_mission_service, base_path="/api"
).register_routes()
CompleteMissionController(
    app=app, use_case_factory=get_mission_service, base_path="/api"
).register_routes()

ListRewardsController(
    app=app, use_case_factory=get_reward_service, base_path="/api"
).register_routes()
GetRewardController(
    app=app, use_case_factory=get_reward_service, base_path="/api"
).register_routes()
CreateRewardController(
    app=app, use_case_factory=get_reward_service, base_path="/api"
).register_routes()
PurchaseRewardController(
    app=app, use_case_factory=get_reward_service, base_path="/api"
).register_routes()

HealthCheckController(app=app, base_path="/api").register_routes()


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=True)
