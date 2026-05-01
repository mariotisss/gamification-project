# KISS Controller Structure Architecture

This document summarizes the current controller approach for the FastAPI backend. Controllers are driving adapters in the hexagonal architecture: they receive HTTP requests, call application use cases, translate domain results into DTO responses, and map expected exceptions into HTTP responses.

## 1. Directory Organization

Controllers are no longer grouped under one generic `gamification_system/infrastructure/driving/api/` folder. After the backend refactor, each bounded system owns its controllers inside its own infrastructure layer.

```text
src/backend/core/pkg/
├── user_system/
│   └── infrastructure/driving/
│       ├── api/
│       │   ├── create_user_controller.py
│       │   ├── get_user_controller.py
│       │   └── list_users_controller.py
│       └── dtos/user_dtos.py
├── mission_system/
│   └── infrastructure/driving/
│       ├── api/
│       │   ├── complete_mission_controller.py
│       │   ├── create_mission_controller.py
│       │   ├── get_mission_controller.py
│       │   └── list_active_missions_controller.py
│       └── dtos/mission_dtos.py
├── reward_system/
│   └── infrastructure/driving/
│       ├── api/
│       │   ├── create_reward_controller.py
│       │   ├── get_reward_controller.py
│       │   ├── list_rewards_controller.py
│       │   └── purchase_reward_controller.py
│       └── dtos/reward_dtos.py
└── shared/
    └── infrastructure/driving/
        ├── api/health_check_controller.py
        └── dtos/
```

This keeps each system self-contained and avoids a single large API package with mixed responsibilities.

## 2. One Controller Per Endpoint

Each endpoint lives in its own controller file. For example, the user API is split into:

- `create_user_controller.py`
- `get_user_controller.py`
- `list_users_controller.py`

This keeps files small, focused, and easier to modify without affecting unrelated endpoints.

## 3. Controller Class Pattern

Every controller file exposes one controller class. The class receives dependencies through its constructor and registers its route through `register_routes()`.

### Key Characteristics

- No global router instances.
- Controllers receive the `FastAPI` application instance directly.
- Controllers receive the exact use case interface they need.
- Routes are registered explicitly from `src/backend/main.py`.
- The URL prefix is injected through `base_path`, currently `/api`.

Example:

```python
class GetUserController:
    def __init__(
        self,
        app: FastAPI,
        use_case: UserUseCases,
        base_path: str,
    ) -> None:
        self.app = app
        self.use_case = use_case
        self.base_path = base_path

    def register_routes(self) -> None:
        @self.app.get(path=f"{self.base_path}/users/{{user_id}}")
        def handle_get_user(user_id: UUID) -> JSONResponse:
            user = self.use_case.get_user(user_id=user_id)
            response_data = build_response(user=user).model_dump(mode="json")
            return JSONResponse(status_code=200, content=response_data)
```

## 4. DTO Organization and Mapping

DTO classes are now separated from controller files and live under each system's `infrastructure/driving/dtos/` folder.

Examples:

- `user_system/infrastructure/driving/dtos/user_dtos.py`
- `mission_system/infrastructure/driving/dtos/mission_dtos.py`
- `reward_system/infrastructure/driving/dtos/reward_dtos.py`

Controllers still own the mapping between domain entities and external response DTOs. For simple responses, the DTO may be constructed directly in the handler. For repeated or larger mappings, the controller uses a local helper such as `build_response()` inside `register_routes()`.

```python
def build_response(user: User) -> UserResponse:
    return UserResponse(
        id=str(user.id),
        username=user.username,
        email=user.email,
        xp=user.xp,
        level=user.level,
        dev_coins=user.dev_coins,
        created_at=user.created_at.isoformat(),
    )
```

The important rule is that domain entities are not returned directly from controllers. HTTP responses should be shaped through explicit DTOs.

## 5. Error Handling

Controllers translate expected domain/application exceptions into HTTP responses near the route handler.

Current examples:

- `EntityNotFoundError` → `404 Not Found`
- `MissionAlreadyCompletedError` → `409 Conflict`
- `InsufficientCoinsError` → `400 Bad Request` or another endpoint-specific client error
- Unexpected exceptions are logged and returned as `500 Internal Server Error`

This keeps HTTP-specific behavior in the driving adapter layer instead of leaking it into domain or application services.

## 6. Main Initialization

The application entry point manually wires dependencies and registers routes.

```python
app = FastAPI(...)

ListUsersController(app=app, use_case=user_service, base_path="/api").register_routes()
GetUserController(app=app, use_case=user_service, base_path="/api").register_routes()
CreateUserController(app=app, use_case=user_service, base_path="/api").register_routes()

HealthCheckController(app=app, base_path="/api").register_routes()
```

The wiring flow is:

1. Instantiate driven adapters, such as in-memory repositories.
2. Inject repositories into application services.
3. Inject services into controllers.
4. Register all controller routes on the FastAPI app.

## 7. Current Direction

The controller design remains intentionally simple. The current preferred structure is:

- System-owned controllers, not one global API module.
- One endpoint per controller file.
- Explicit constructor dependency injection.
- DTOs separated into `dtos/` files.
- Mapping kept close to the controller.
- Manual route registration in `main.py` until the project needs a more advanced composition mechanism.
