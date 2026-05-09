# How to Unit Test the Backend

This guide explains how to run the backend unit test suite locally.

## Prerequisites

- The backend virtual environment already created and dependencies installed (see `how-to-run-backend.md`).
- A terminal opened at the project root.

The test suite uses `pytest` and FastAPI's `TestClient` (which depends on `httpx`).

## 1. Install Test Dependencies

From the project root, with the backend virtual environment active:

```bash
pip install pytest httpx
```

`pytest` is already declared in the backend environment, but `httpx` is required by `fastapi.testclient.TestClient` and must be present.

## 2. Run the Full Test Suite

From `src/backend/`:

```bash
cd src/backend
.venv/bin/pytest tests/ -v
```

You should see all unit tests pass in well under a second.

## 3. Run a Subset of Tests

Run only unit tests:

```bash
.venv/bin/pytest tests/unit -v
```

Run only one system:

```bash
.venv/bin/pytest tests/unit/mission_system -v
```

Run a single file:

```bash
.venv/bin/pytest tests/unit/user_system/domain/entities/test_user.py -v
```

Run a single test function by keyword match:

```bash
.venv/bin/pytest -k "complete_mission_then_awards_xp" -v
```

## Notes

- Tests use `pytest`'s automatic discovery, configured by `src/backend/pytest.ini`.
- `tests/integration/` is reserved for cross-system tests and is currently empty.
- Tests run against in-memory repositories, so they are fast and deterministic, with no external dependencies.
