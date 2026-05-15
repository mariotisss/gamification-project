# Progress Summary - Phase 1: Backend PostgreSQL Adapters

This step replaces the in-memory repository adapters with PostgreSQL-backed adapters across `user_system`, `mission_system`, and `reward_system`. The hexagonal architecture, port contracts, and the 90-test unit suite are all preserved; persistence becomes a real, durable concern without leaking any database concept into the domain.

## 1. Decisions

The shape of the implementation comes from a small set of upfront decisions:

| Decision           | Choice                                                  | Why                                                                                                       |
| ------------------ | ------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| Database           | **PostgreSQL 16**                                       | Single source of truth, ACID for the DevCoin economy, room to grow (JSONB, window functions, FKs).        |
| Driver             | **psycopg 3 (sync)**                                    | Handlers and ports were already sync; keeps every signature unchanged.                                    |
| ORM                | **SQLAlchemy 2.0 (sync)**                               | Mature, full control, declarative mappers — ORM models live only in `infrastructure/`, domain stays pure. |
| Migrations         | **Alembic**                                             | Default companion to SQLAlchemy.                                                                          |
| Connection mgmt    | One `Engine` + per-request `Session` via FastAPI `Depends` | Natural fit for the per-request unit-of-work needed by cross-aggregate writes.                            |
| Domain entities    | **Unchanged**                                           | Domain must not import SQLAlchemy.                                                                        |
| Port signatures    | **Unchanged**                                           | Postgres adapter is a drop-in.                                                                            |
| In-memory repos    | **Kept**                                                | Unit tests keep their sub-second feedback loop.                                                           |
| Local DB           | **Docker Compose `postgres:16`**                        | Reproducible across machines.                                                                             |
| Integration tests  | **`testcontainers-python`**                             | Real Postgres in CI without external infra.                                                               |

## 2. Directory Layout

A new top-level technical-infrastructure tree was added at `src/backend/core/infrastructure/`, separate from the domain-oriented `core/pkg/`. ORM models, however, live with the system that owns the table — they are driven adapters of that system's repository port.

```
src/backend/
├── core/
│   ├── infrastructure/persistence/          (NEW — technical platform)
│   │   ├── settings.py                      (DatabaseSettings, pydantic-settings)
│   │   ├── database.py                      (engine + session factory + session_scope)
│   │   ├── base.py                          (declarative Base, shared metadata)
│   │   └── session_dependency.py            (FastAPI per-request provider)
│   └── pkg/
│       ├── user_system/infrastructure/driven/
│       │   ├── adapters/
│       │   │   ├── in_memory_user_repository.py
│       │   │   └── postgres_user_repository.py    (NEW)
│       │   └── persistence/models/user_model.py   (NEW)
│       ├── mission_system/infrastructure/driven/
│       │   ├── adapters/
│       │   │   ├── in_memory_mission_repository.py
│       │   │   └── postgres_mission_repository.py (NEW)
│       │   └── persistence/models/
│       │       ├── mission_model.py
│       │       └── mission_completion_model.py
│       └── reward_system/infrastructure/driven/
│           ├── adapters/
│           │   ├── in_memory_reward_repository.py
│           │   └── postgres_reward_repository.py  (NEW)
│           └── persistence/models/reward_model.py (NEW)
├── alembic.ini                              (NEW)
├── alembic/                                 (NEW)
│   ├── env.py
│   ├── script.py.mako
│   └── versions/0001_initial_schema.py
└── tests/integration/
    ├── conftest.py                          (NEW — testcontainers fixture)
    └── persistence/
        ├── test_postgres_user_repository.py
        ├── test_postgres_mission_repository.py
        └── test_postgres_reward_repository.py
```

All ORM models register on the same `Base.metadata` imported from `core/infrastructure/persistence/base.py`, so Alembic autogenerate, FK resolution, and `metadata.create_all` work normally. Cross-system FKs (`mission_completions.user_id → users.id`) use string targets to avoid cross-system Python imports.

## 3. Dependencies

Both `pyproject.toml` and `src/backend/requirements.txt` were updated to add the runtime stack and test container support:

- **Runtime:** `sqlalchemy>=2.0.36`, `psycopg[binary]>=3.2.3`, `alembic>=1.14.0`, `pydantic-settings>=2.6.0`.
- **Dev:** `testcontainers[postgres]>=4.8.2`.

Existing constraints in `requirements.txt` (which is the source of truth for version pins) were preserved; `pyproject.toml` was realigned to match them.

## 4. Configuration

`DatabaseSettings` uses `pydantic-settings` with the `GAMIF_DB_` env prefix and reads an optional `.env` file. Defaults match `docker-compose.yml`, so local development works out of the box without a `.env`:

```python
host: str = "localhost"
port: int = 5432
user: str = "gamif"
password: str = "gamif"
name: str = "gamif"
```

A `docker-compose.yml` at the repo root brings up `postgres:16` with a healthcheck, and `.env.example` documents the overridable variables for environments that need them.

> Defaults are convenient but not safe outside local dev — see `docs/tech-debt.md` item #1.

## 5. Engine and Session

`database.py` exposes three primitives:

- `build_engine(settings)` — single `Engine` for the process, with configurable pool size and SQL echo.
- `build_session_factory(engine)` — `sessionmaker` with `autoflush=False` and `expire_on_commit=False`.
- `session_scope(factory)` — context manager: commit on success, rollback on exception, close at the end.

`session_dependency.py` wraps the factory in a `SessionProvider` whose `.get` method is a FastAPI generator dependency: yield the session, commit on the way out, rollback on any exception. This is the transaction boundary for every HTTP request.

## 6. ORM Models

Each table is represented by a SQLAlchemy 2.0 declarative model in the appropriate system's `infrastructure/driven/persistence/models/` folder:

- `UserModel` — `users(id uuid PK, username UNIQUE, email UNIQUE, xp, level, dev_coins, created_at)`.
- `MissionModel` — `missions(id uuid PK, title, description, xp_reward, coin_reward, is_active)`.
- `MissionCompletionModel` — `mission_completions(id uuid PK, user_id FK→users, mission_id FK→missions, completed_at)` with a `UniqueConstraint(user_id, mission_id)`.
- `RewardModel` — `rewards(id uuid PK, name, description, cost, reward_type)`.

The unique constraint on `(user_id, mission_id)` makes the "mission already completed" rule race-safe at the database level (see §8).

## 7. Postgres Adapters

Each Postgres adapter implements the same port as its in-memory sibling and keeps the mapper functions (`_to_domain`, `_to_model`) private to the file. The mappers translate between SQLAlchemy models and the domain dataclasses — no leaky abstraction is exposed.

Example contract for users (same shape for missions and rewards):

```python
class PostgresUserRepository(UserRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def get_by_id(self, user_id: UUID) -> User | None: ...
    def get_all(self) -> list[User]: ...
    def save(self, user: User) -> User: ...
    def update(self, user: User) -> User: ...
```

Note: `get_by_id` keeps the `User | None` return because the existing port demands it — see `docs/tech-debt.md` item #6.

## 8. Transaction Boundary and Idempotency

Two service methods write to multiple aggregates:

- `MissionService.complete_mission` → updates `User` (+xp/+coins) **and** inserts a `MissionCompletion`.
- `RewardService.purchase_reward` → updates `User` (-coins) and reads a `Reward`.

These need to be atomic. The strategy:

1. **One `Session` per HTTP request**, provided by `SessionProvider.get` via `Depends`.
2. **All Postgres adapters used in a request share that session**, passed in via constructor.
3. **Commit happens at the end of the dependency** on success; **rollback** on any raised exception.
4. **Services know nothing about sessions.** They depend on ports and only see domain objects.

Additionally, `MissionCompletionModel` has `UniqueConstraint(user_id, mission_id)`. The service's existing fast-path check (`get_completions_by_user` + `any`) stays as the happy-path optimization, but the database constraint is the race-safe backstop:

```python
def save_completion(self, completion: MissionCompletion) -> MissionCompletion:
    self._session.add(instance=_completion_to_model(entity=completion))
    try:
        self._session.flush()
    except IntegrityError as exc:
        raise MissionAlreadyCompletedError(
            user_id=completion.user_id, mission_id=completion.mission_id
        ) from exc
    return completion
```

If two concurrent requests slip past the fast-path check, Postgres rejects the second insert and the adapter translates that into the same domain exception the service would have raised. Hexagonal cleanliness is preserved.

The equivalent backstop for coin balances does **not** exist yet — see `docs/tech-debt.md` item #7.

## 9. DI Rewire — Controllers as Factories

In Phase 1 each controller received its `UseCases` instance once at construction time and closed over it in the route handler. That doesn't fit a per-request session: services need to be rebuilt for each request so they can be wired with the right session-bound repositories.

The change is mechanical but touches all 11 controllers:

- **Before:** `__init__(app, use_case, base_path)`; handler uses `self.use_case`.
- **After:** `__init__(app, use_case_factory, base_path)`; handler receives `use_case = Depends(self.use_case_factory)`.

`main.py` then defines three per-request factories (one per system) that take `Session = Depends(session_provider.get)` and assemble the services with Postgres adapters. The controllers receive the factories at registration time:

```python
ListUsersController(app=app, use_case_factory=get_user_service, base_path="/api").register_routes()
# … 11 controllers total, same pattern
```

The `HealthCheckController` is unchanged — it has no dependencies.

The existing controller unit tests were updated to pass `use_case_factory=lambda: mock` instead of `use_case=mock`. No other test code changed, and all 90 unit tests still pass in well under a second.

## 10. Alembic

- `alembic.ini` lives at `src/backend/alembic.ini`.
- `alembic/env.py` imports `Base` and all four ORM model modules, then reads the database URL from `DatabaseSettings()` so migrations always target the same DB the app does.
- `alembic/versions/0001_initial_schema.py` is the hand-written initial migration: four tables, two unique constraints on `users`, the composite unique constraint on `mission_completions`, and `ON DELETE CASCADE` FKs into `users` and `missions`.

Day-to-day workflow: `cd src/backend && .venv/bin/alembic upgrade head`.

## 11. Integration Tests

`tests/integration/conftest.py` brings up a single `PostgresContainer` per test session, builds an engine pointed at it, and provisions schema directly via `Base.metadata.create_all`. A function-scoped `session` fixture yields a clean SQLAlchemy `Session`, rolls back, truncates every table, and closes — so each test starts from an empty database.

Three test modules exercise the Postgres adapters end to end:

- `test_postgres_user_repository.py` — `save`, `get_by_id`, `get_all`, `update` (including xp/level recomputation), missing-id behavior.
- `test_postgres_mission_repository.py` — `save`, `get_all_active` filters inactive missions, `save_completion`/`get_completions_by_user`, and the duplicate-completion → `MissionAlreadyCompletedError` translation through the unique constraint.
- `test_postgres_reward_repository.py` — `save`, `get_by_id`, `get_all` ordered by cost, missing-id behavior.

These tests are not run as part of the default unit suite. They require Docker to be available. Run them from `src/backend/` with:

```bash
.venv/bin/python -m pytest tests/integration -q
```

## 13. Local Workflow

End-to-end loop on a developer laptop:

```bash
# 1. Start Docker (Colima or Docker Desktop)
colima start

# 2. Bring up Postgres
docker-compose up -d postgres

# 3. Install deps (one-off)
cd src/backend
source .venv/bin/activate
pip install -r requirements.txt

# 4. Apply schema
alembic upgrade head                    # check with: docker-compose exec postgres psql -U gamif -d gamif -c '\dt'

# 5. Run the API
python main.py                          # or: uvicorn main:app --reload

# 6. Tests
python -m pytest tests/unit -q          # ~0.3s, no Postgres
python -m pytest tests/integration -q   # spins up its own Postgres via testcontainers

# 7. Manual API exercise
# Open Bruno → bruno/ → environment "Local" → run requests
```

Persistence sanity check: after the smoke run, restart the API (`Ctrl-C` then re-launch) and the previously created users, missions, and rewards are still there — confirming the in-memory era is over.

## 14. Acceptance Criteria — Results

| Criterion                                                           | Status                                                                                                                  |
| ------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------- |
| `docker compose up -d postgres` brings up Postgres on `:5432`       | ✅                                                                                                                       |
| `alembic upgrade head` creates all four tables                      | ✅                                                                                                                       |
| `uvicorn main:app --reload` starts the API; `/api/health` returns OK | ✅                                                                                                                       |
| All 90 unit tests still pass, sub-second                            | ✅ `90 passed in 0.33s`                                                                                                  |
| Integration tests pass against testcontainers Postgres              | ✅ (require Docker)                                                                                                      |
| End-to-end smoke: create user → mission → complete → repeat → 409   | ✅ (Bruno + curl)                                                                                                        |
| Restart the API: previously created data persists                   | ✅                                                                                                                       |
| `ruff` clean, `pyright` clean                                       | Not re-verified in this step; out-of-scope for the persistence work itself.                                              |

## Result

The backend now persists every domain entity to PostgreSQL, with a transaction boundary that spans cross-aggregate writes, a race-safe backstop for the "mission already completed" rule, and a clean separation between the new technical-infrastructure tree and the per-system bounded contexts. The hexagonal architecture survived intact: the only application-layer change was registering controllers with a `use_case_factory` instead of a pre-built service, and even that change preserved the in-memory path for unit tests. The next phase can build on this foundation without revisiting persistence.
