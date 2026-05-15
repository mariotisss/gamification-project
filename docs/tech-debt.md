# Tech Debt

Known gaps, deferred work, and risks in the current implementation. Each item lists severity, why it exists, and what to do about it. Keep this file updated as items are resolved or new debt is taken on.

Severity legend:
- 🔴 **Critical** — would bite in production today.
- 🟡 **Architectural** — known design gap, plan acknowledges it.
- 🟢 **Minor** — nice-to-have or low impact.

---

## 🔴 Critical

### 1. Hardcoded database credentials in defaults

**Where:** `src/backend/core/infrastructure/persistence/settings.py`

`DatabaseSettings` ships with default values `host=localhost`, `user=gamif`, `password=gamif`, `name=gamif`. These match `docker-compose.yml` so local dev "just works" without a `.env` file — but it also means the app will boot with these defaults anywhere the env isn't overridden.

**Risk:** If this is ever deployed to a reachable network without `GAMIF_DB_*` env vars set, the database is wide open with predictable credentials.

**Fix:** Remove the default password (and ideally user/name). Make them required env values so missing config raises on startup instead of silently using a known-bad default.

---

### 2. No authentication, authorization, rate limiting, or CORS

**Where:** All controllers under `core/pkg/*/infrastructure/driving/api/`.

Anyone who can reach the HTTP port can:
- Create arbitrary users.
- Call `POST /api/missions/{id}/complete` with **any** `user_id` in the body — no verification that the caller is that user.
- Call `POST /api/rewards/{id}/purchase` with any `user_id` and drain their coins.

**Risk:** Trivial abuse of the DevCoin economy; no audit trail of who did what.

**Fix:** Add an auth dependency (API key for now, real session/JWT later) on all mutating endpoints. Derive `user_id` from the authenticated principal, not the request body.

---

### 3. Integration tests bypass Alembic

**Where:** `src/backend/tests/integration/conftest.py`

The `engine` fixture calls `Base.metadata.create_all(bind=engine)` to build the schema directly from the ORM models. The actual migration file (`alembic/versions/0001_initial_schema.py`) is **never exercised by tests**.

**Risk:** A wrong, missing, or out-of-sync migration would pass CI and only fail in production when `alembic upgrade head` runs against a real DB.

**Fix:** Replace `create_all` with `alembic.command.upgrade(cfg, "head")` pointing at the testcontainer URL. Tests then validate the migration, not just the models.

---

### 4. No migration version check at startup

**Where:** `src/backend/main.py`

The API starts and serves traffic regardless of the DB schema state. If the code expects migration `0005` but the DB is at `0003`, the app boots and breaks on the first query.

**Risk:** Deploys that forget `alembic upgrade head` produce confusing runtime errors instead of failing fast.

**Fix:** On startup, compare `alembic current` to `alembic heads`. If they differ, refuse to serve (or log a loud warning, depending on policy).

---

### 5. Overly broad `except Exception` → 500

**Where:** Every controller. Example: `create_user_controller.py`.

```python
except Exception as e:
    logger.error(f"Error creating user: {e}")
    return JSONResponse(status_code=500, ...)
```

A real bug and a normal business condition (e.g. `IntegrityError` from a duplicate email/username) both become opaque 500s, obscuring root cause and confusing clients.

**Risk:** Duplicate-email signups look like server errors. Real 500s get lost in the noise.

**Fix:** Narrow the catches. At minimum:
- Map `sqlalchemy.exc.IntegrityError` on user creation → 409 with a clean message.
- Let true unexpected exceptions propagate to a FastAPI exception handler that logs the full traceback and returns 500.

---

## 🟡 Architectural (plan §13 acknowledges)

### 6. Repository ports return `Entity | None`

**Where:** `core/pkg/*/domain/ports/driven/*_repository.py`

`get_by_id` is typed `User | None` (and equivalents). This violates the project's `python-none-usage-restriction.md` rule that external return types must not be `None`.

**Risk:** Inconsistent with project conventions; every caller must None-check.

**Fix (deferred to a dedicated refactor):** Either split into `get_by_id` + `exists`, or introduce an `UNKNOWN` sentinel on the entity, or raise `EntityNotFoundError` at the port level (currently raised at the service level).

---

### 7. No optimistic locking on `users.dev_coins`

**Where:** `core/pkg/user_system/infrastructure/driven/persistence/models/user_model.py` + `PostgresUserRepository.update`.

Two concurrent `purchase_reward` (or `complete_mission`) calls for the same user can:
1. Both read `dev_coins=100`.
2. Both decide they have enough.
3. Both write the deducted value.

Result: the user "spent" 100 coins but only one deduction landed.

**Risk:** Coin balance corruption under concurrency. The `MissionCompletion` unique constraint covers completion idempotency; **balance has no equivalent backstop.**

**Fix (deferred to Phase 2):** Add a `version int` column, increment it on every update, and use `WHERE id = :id AND version = :v` — retry on zero affected rows.

---

### 8. Service-layer email/username uniqueness check is missing

**Where:** `UserService.create_user`.

The DB enforces `UNIQUE` on `username` and `email`, but the service doesn't check before insert. Duplicate creation falls through the generic `except Exception` and surfaces as 500 (see item #5).

**Fix:** Either pre-check at the service layer with a domain exception, or catch `IntegrityError` at the controller layer and translate to 409. The latter is race-safe; the former is more explicit.

---

### 9. Connection pool defaults are dev-sized

**Where:** `DatabaseSettings.pool_size=5`, `max_overflow=10`.

Fine for a single uvicorn worker on a laptop. Multiple workers × multiple replicas will exhaust Postgres's default `max_connections=100` quickly.

**Fix:** Revisit when scaling out. Likely needs a per-environment override and a PgBouncer in front of Postgres.

---

### 10. No async path

**Where:** Whole stack is sync (`def` handlers, sync SQLAlchemy, sync `psycopg`).

**Why:** Intentional Phase 1 decision. Async would have required touching every signature.

**Fix:** Phase 2 re-evaluates async + a task queue (procrastinate/Celery) for event processing.

---

## 🟢 Minor

### 11. No request-level idempotency keys

`POST /api/missions/{id}/complete` is idempotent at the DB level via the unique constraint, but a client retry on a transient network failure has no way to distinguish "the original succeeded" from "the original failed; this is the first real attempt." Same for `purchase_reward`.

**Fix:** Accept an `Idempotency-Key` header and persist results keyed by it for some TTL.

---

### 12. No structured logging

Standard library logging with f-strings. No correlation IDs, no JSON output, no log levels per module.

**Fix:** Adopt `structlog` or similar; add a request-ID middleware.

---

### 13. `.env` resolution is CWD-dependent

`pydantic-settings` looks for `.env` relative to the process's working directory. Running `alembic` or `python main.py` from any directory other than `src/backend/` silently falls back to defaults.

**Fix:** Either pin the env file path absolutely in `SettingsConfigDict`, or document the constraint loudly in the README/runbook.

---

## What's solid (intentionally listed so we don't regress)

- **Transaction boundary** — `SessionProvider.get()` commits on success, rolls back on any exception. Multi-aggregate writes (`complete_mission`, `purchase_reward`) are atomic per request.
- **Idempotency backstop for completions** — `uq_mission_completion_user_mission` + `IntegrityError → MissionAlreadyCompletedError` mapping handles the TOCTOU race between the service's fast-path check and the insert.
- **Hexagonal isolation** — domain has zero SQLAlchemy imports. The Postgres adapter can be swapped for anything else without touching services.
- **Test layering** — 90 unit tests stay sub-second on in-memory repos; integration tests use real Postgres via testcontainers.

---

## Suggested order of attack

Quick wins (an afternoon each):
1. Item #1 — remove default password.
2. Item #3 — integration tests run real migrations.
3. Item #4 — startup migration check.
4. Item #5 — narrow `except Exception`, map `IntegrityError`.

Bigger pieces (each its own PR with design discussion):
5. Item #2 — auth model.
6. Item #7 — optimistic locking strategy.
7. Item #6 — repository port refactor.
