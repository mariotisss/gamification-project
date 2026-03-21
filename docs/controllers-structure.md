# KISS Controller Structure Architecture

This document summarizes the architectural approach for building controllers (driving adapters) in this service following a KISS (Keep It Simple, Stupid) philosophy.

## 1. Directory Organization
Controllers are strictly organized by domain module inside the infrastructure layer (`driving/api`). Each module has its own dedicated subdirectory:
```text
infrastructure/driving/api/
├── health/
├── mission/
├── reward/
└── user/
```

## 2. One Controller Per File
Instead of grouping multiple endpoints into a single, massive router file, **every single endpoint is placed in its own file**. 

For example, the `user` module is split into:
- `create_user_controller.py`
- `get_user_controller.py`
- `list_users_controller.py`

This ensures that files stay incredibly small, focused, and easy to maintain.

## 3. The Controller Class Pattern
Every file exposes a single Controller Class. The class relies entirely on **Explicit Dependency Injection** via its `__init__` constructor.

### Key Characteristics:
* **No global router instances:** Controllers take the `FastAPI` application instance directly.
* **Explicit Use Case Injection:** The controller receives the exact domain Use Case it needs to perform its job.
* **Separation of Router Definition:** The endpoints are wired to the `FastAPI` app explicitly by calling the `.register_routes()` instance method.

```python
class GetUserController:
    def __init__(self, app: FastAPI, use_case: UserUseCases, base_path: str) -> None:
        self.app = app
        self.use_case = use_case
        self.base_path = base_path

    def register_routes(self) -> None:
        @self.app.get(path=f"{self.base_path}/users/{{user_id}}")
        def handle_get_user(user_id: UUID) -> JSONResponse:
            # ... Endpoint Logic
```

## 4. Inline Data Transfer Objects (DTO) Mapping
To avoid creating cluttered "mapper" directories with fragmented translation logic, the mapping from Domain Entities to external Pydantic DTOs is handled **inline within the `register_routes` method** as a nested helper function.

This ensures that the representation of the response lives exactly where the response is generated:
```python
    def register_routes(self) -> None:
        @self.app.get(...)
        def handle_get_user(user_id: UUID) -> JSONResponse:
            user = self.use_case.get_user(user_id=user_id)
            response_data = build_response(user=user).model_dump(mode="json")
            return JSONResponse(status_code=200, content=response_data)

        # ── Inline Mapping Logic ──
        def build_response(user: User) -> UserResponse:
            return UserResponse(
                id=str(user.id),
                username=user.username,
                email=user.email,
                # ...
            )
```

## 5. Main Initialization
In the application's entry point (`main.py`), routing is handled safely and structurally by creating instances of these controllers and registering their routes on the fly:

```python
app = FastAPI(...)

GetUserController(app=app, use_case=user_service, base_path="/api").register_routes()
CreateUserController(app=app, use_case=user_service, base_path="/api").register_routes()
# ... 
```
