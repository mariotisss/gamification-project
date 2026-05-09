# Progress Summary - Phase 1: Backend Unit Tests

This step introduces the first test suite for the backend. The goal was to add unit-level coverage on every layer of every system without changing production code, and to organize tests so that they mirror the same hexagonal architecture used by `src/backend/core/pkg/`.

## 1. Test Framework and Configuration

`pytest` is used as the only test framework. A `pytest.ini` was added at `src/backend/` to define test discovery rules:

```ini
[pytest]
testpaths = tests
pythonpath = .
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -ra
```

`pythonpath = .` lets test modules import from `core.pkg.*` exactly the same way the application does, without packaging tweaks.

`httpx` was added to the virtual environment so that FastAPI's `TestClient` can drive the controllers end to end.

## 2. Test Folder Layout

Tests live under `src/backend/tests/`, split into `unit/` and `integration/`. Integration tests are reserved for cross-system scenarios and are intentionally empty for now.

```text
src/backend/tests/
├── conftest.py
├── integration/                (placeholder)
└── unit/
    ├── mission_system/
    ├── reward_system/
    ├── user_system/
    └── shared/
```

Inside each system, the test tree mirrors the production hexagonal layout:

```text
<system>/
├── conftest.py
├── domain/
│   ├── entities/
│   └── exceptions/
├── application/
│   └── use_cases/
└── infrastructure/
    ├── driven/adapters/
    └── driving/api/
```

This makes it trivial to find the test that covers any production file: the path under `tests/unit/` is the same as the path under `core/pkg/`.

## 3. Naming Convention

Every test function follows the `given / when / then` pattern, written in snake case:

```text
test_given_<state>_when_<action>_then_<expected_outcome>
```

Examples:

- `test_given_unknown_user_when_complete_mission_then_raises_entity_not_found_for_user`
- `test_given_insufficient_coins_when_post_purchase_then_returns_402`
- `test_given_user_when_add_xp_crosses_100_threshold_then_level_increments`

The format documents the scenario directly in the failure message, so a test name alone explains what is being verified without opening the file.

## 4. Layer-by-Layer Approach

Each layer is tested with a strategy aligned with its responsibility:

- **Domain entities**: pure assertions, no doubles. The richest set of domain tests lives in `user_system`, since `User` is the only entity with real behavior (`add_xp`, `add_dev_coins`, `deduct_dev_coins`, level recalculation).
- **Domain exceptions**: validate the message format, public attributes, and that they subclass `Exception`.
- **Application services**: exercised against the real `InMemory*Repository` adapters. This avoids over-mocking and keeps tests close to how the system actually composes at runtime, while still being fast and deterministic.
- **Driven adapters (in-memory repositories)**: tested in isolation to confirm storage, retrieval, filtering, and update semantics.
- **Driving adapters (controllers)**: instantiated against a fresh `FastAPI()` app with a `Mock(spec=<UseCases port>)` and exercised through `TestClient`. Each controller is verified for happy path, validation errors (`422`), domain errors (`404`, `409`, `402`), and unexpected errors (`500`).

## 5. Shared Fixtures

Each system has its own `conftest.py` that provides the building blocks the tests need:

- `mission_system/conftest.py`: fresh `InMemoryMissionRepository`, fresh `InMemoryUserRepository`, a wired `MissionService`, plus `seeded_user` and `seeded_mission` factories.
- `reward_system/conftest.py`: fresh repositories, a wired `RewardService`, and a `seeded_user` already loaded with DevCoins so purchase scenarios are easy to express.
- `user_system/conftest.py`: fresh `InMemoryUserRepository` and `UserService`.

This keeps the actual test functions short and focused on the assertion they care about.

## 6. Coverage Summary

The suite has **90 unit tests**, all green:

| System           | Tests | Layers covered                                                       |
| ---------------- | ----- | -------------------------------------------------------------------- |
| `mission_system` | 33    | entity, exception, service, in-memory repo, 4 controllers            |
| `reward_system`  | 24    | entity, exception, service, in-memory repo, 4 controllers            |
| `user_system`    | 24    | entity (full business logic), service, in-memory repo, 3 controllers |
| `shared`         | 4     | `EntityNotFoundError`, health check controller                       |

`MissionCompletion` has no behavior of its own and is exercised transitively through `MissionService` tests, so it does not need a dedicated entity test.

## 7. Running the Suite

From `src/backend/`:

```bash
.venv/bin/pytest tests/ -v          # full suite
.venv/bin/pytest tests/unit -v      # only unit tests
```

A typical local run completes in well under a second, which keeps the feedback loop tight while the project is still in Phase 1.

## Result

The backend now has a fast, deterministic unit test suite that mirrors the hexagonal layout of the production code one-to-one. Each layer is verified with the strategy that best fits it, every test name reads as a `given / when / then` scenario, and the `tests/integration/` folder is in place to host cross-system tests as the project moves into the next phases.
