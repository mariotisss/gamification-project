# Tech Debt

Known gaps, deferred work, and risks in the current implementation. Each item lists severity, why it exists, and what to do about it. Keep this file updated as items are resolved or new debt is taken on.

Severity legend:
- 🔴 **Critical** — would bite in production today.
- 🟡 **Architectural** — known design gap, plan acknowledges it.
- 🟢 **Minor** — nice-to-have or low impact.

---

## 🔴 Critical

### 1. ~~Hardcoded database credentials in defaults~~ ✅ Resolved (2026-05-17)

**Where:** `src/backend/core/infrastructure/persistence/settings.py`

`DatabaseSettings` no longer ships defaults for `user`, `password`, or `name`. Missing config now raises a `pydantic.ValidationError` on startup. Local development relies on a gitignored `.env` at the repo root (template: `.env.example`); `DatabaseSettings` resolves the file path relative to the source tree, so it works from any CWD. Only the non-secret network locators (`host=localhost`, `port=5432`) and operational toggles (`echo`, `pool_size`, `max_overflow`) keep defaults.

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

### 3. ~~Integration tests bypass Alembic~~ ✅ Resolved (2026-05-17)

**Where:** `src/backend/tests/integration/conftest.py`

The `engine` fixture now runs `alembic.command.upgrade(config, "head")` against the testcontainer URL instead of `Base.metadata.create_all`. Tests exercise the same migration files that production runs, so a broken or missing migration breaks CI rather than surviving until deploy.

---

### 4. ~~No migration version check at startup~~ ✅ Resolved (2026-05-17)

**Where:** `src/backend/main.py`, `src/backend/core/infrastructure/persistence/migration_check.py`

On startup, FastAPI's `lifespan` calls `assert_schema_up_to_date(engine)`, which compares `MigrationContext.get_current_revision()` against `ScriptDirectory.get_current_head()`. A mismatch raises `SchemaOutOfDateError` and the app refuses to serve traffic — the developer sees a clear "run `alembic upgrade head`" message instead of confusing runtime errors on the first query.

---

### 5. ~~Overly broad `except Exception` → 500~~ ✅ Resolved (2026-05-17) — partial

**Where:** `create_user_controller.py`, `postgres_user_repository.py`.

A new domain exception `UserAlreadyExistsError` was introduced. `PostgresUserRepository.save` now catches `IntegrityError` (raised when the `users.username` or `users.email` unique constraint is violated) and translates it into the domain exception — race-safe via the DB constraint, same pattern as `MissionAlreadyCompletedError` on `mission_completions`. `CreateUserController` catches `UserAlreadyExistsError` → 409, before falling through to the generic `except Exception` → 500. Duplicate signups now produce a clean 409 with a meaningful message.

> **Scope note:** the broad `except Exception → 500` is still present in all controllers as a last-line defense. It's no longer hiding the most common business case (duplicate user), but a cleaner approach — global FastAPI exception handler + removal of the per-controller broad catch — is still open work.

---

## 🟡 Architectural (plan §13 acknowledges)

### 6. ~~Repository ports return `Entity | None`~~ ✅ Resolved (2026-05-18)

**Where:** `core/pkg/*/domain/ports/driven/*_repository.py`

`get_by_id` now returns `Entity` (not `Entity | None`). Both Postgres and in-memory adapters raise `EntityNotFoundError` themselves when a row is missing; services dropped their `if x is None: raise …` guards. Controllers' existing `except EntityNotFoundError → 404` continues to work — the exception is just raised one layer deeper now. Compliant with `python-none-usage-restriction.md`.

---

### 7. ~~No optimistic locking on `users.dev_coins`~~ ✅ Resolved (2026-05-18)

**Where:** `core/pkg/user_system/infrastructure/driven/persistence/models/user_model.py` + `PostgresUserRepository.update`.

`UserModel` now carries a `version_id` column with `__mapper_args__ = {"version_id_col": version_id}`, so SQLAlchemy emits `WHERE id=:id AND version_id=:read_version` on every flush and auto-bumps the counter. Stale writes raise `StaleDataError`, which the adapter translates into a new domain exception `ConcurrentUserUpdateError`. Both `purchase_reward_controller` and `complete_mission_controller` map it to HTTP 409. Alembic migration `0002_add_user_version_id` adds the column. Retry budget intentionally left to the client — left as an explicit follow-up if needed.

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

### 12. ~~No structured logging~~ ✅ Resolved (2026-05-18)

`structlog` adopted with a minimal pipeline (`merge_contextvars + add_log_level + TimeStamper + ConsoleRenderer`). A FastAPI middleware binds `request_id`, `method`, and `path` as contextvars on every request, so every line in the same request shares the same `request_id`. All 11 controllers + health log INFO on `incoming_*` / `outgoing_*` and ERROR on exception paths; the 3 Postgres adapters log INFO on entry/return and ERROR on translated DB exceptions; `SessionProvider` logs ERROR on rollback; `assert_schema_up_to_date` logs INFO/ERROR.

> **Known gap:** Uvicorn's own loggers (`uvicorn`, `uvicorn.access`) still use stdlib `logging` with their default formatter, so startup and access lines (`INFO:     Application startup complete.`, `INFO:     127.0.0.1:port - "GET ..."`) appear unstructured alongside our structlog output. Routing stdlib `logging` through structlog (`structlog.stdlib.ProcessorFormatter`) is open work for when the app ships externally.

> **PII note:** `create_user` logs `username` and `email` at INFO. Move to DEBUG before external deployment (see CLAUDE.md).

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
1. ~~Item #1 — remove default password.~~ ✅ Done 2026-05-17
2. ~~Item #3 — integration tests run real migrations.~~ ✅ Done 2026-05-17
3. ~~Item #4 — startup migration check.~~ ✅ Done 2026-05-17
4. ~~Item #5 — narrow `except Exception`, map `IntegrityError`.~~ ✅ Done 2026-05-17 (partial — broad catch still present as fallback)

Bigger pieces (each its own PR with design discussion):
5. Item #2 — auth model.
6. ~~Item #7 — optimistic locking strategy.~~ ✅ Done 2026-05-18
7. ~~Item #6 — repository port refactor.~~ ✅ Done 2026-05-18
8. ~~Item #12 — structured logging.~~ ✅ Done 2026-05-18
