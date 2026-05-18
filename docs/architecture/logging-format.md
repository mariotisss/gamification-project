# Logging Format

Convention for structured logging in `src/backend/`. Adopted 2026-05-18 alongside tech-debt item #12.

## Library

`structlog` with a minimal pipeline. Configured once on startup via `core/infrastructure/observability/logging.configure_logging()`:

```python
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.dev.ConsoleRenderer(),
    ],
    cache_logger_on_first_use=True,
)
```

No stdlib `dictConfig`. Uvicorn keeps its own access log format for now (known gap; revisit when shipping externally).

## Where we log: boundaries only

Logging is a boundary concern, not a per-event concern. **Only two layers log**:

1. **Driving boundary — controllers.** Log on entry (`incoming_*`), on success (`outgoing_*`), and inside every `except` clause.
2. **Driven boundary — Postgres adapters.** Log on method entry (`repo_*_called`), on return (`repo_*_returned`), and inside every `except` (translated DB errors).

Plus two infrastructure touch-points:
- `SessionProvider.get()` — ERROR on rollback.
- `assert_schema_up_to_date()` — INFO on success, ERROR on mismatch.

**The application services, domain entities, and in-memory adapters do not log.** The domain stays framework-free; services are observed indirectly through the two boundaries. In-memory adapters are test-only and would just add noise.

## Levels (INFO / DEBUG / ERROR only)

WARNING and CRITICAL are intentionally dropped.

| Level | Use |
|---|---|
| **INFO** | Boundary outcomes worth seeing in normal runs — controller and adapter request/response one-liners, schema-up-to-date on startup. |
| **DEBUG** | Reserved for future application-level diagnostics (use-case decisions, internal state). Not used in Phase 1. |
| **ERROR** | Anything that ends in an exception — expected domain exceptions (`EntityNotFoundError`, `InsufficientCoinsError`, `MissionAlreadyCompletedError`, `ConcurrentUserUpdateError`, `UserAlreadyExistsError`), unhandled exceptions, transaction rollbacks, migration-check failures. |

Same exception may log at ERROR twice — once in the adapter (where it was raised) and once in the controller (where it was mapped to an HTTP status). Both lines carry the same `request_id`; the duplication is intentional and useful.

## Request correlation

A FastAPI middleware binds `request_id`, `method`, and `path` as `structlog` contextvars at the start of every request:

```python
@app.middleware("http")
async def bind_request_context(request, call_next):
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        request_id=str(uuid.uuid4()),
        method=request.method,
        path=request.url.path,
    )
    return await call_next(request)
```

Every line emitted during the request inherits those three fields — no need to pass them explicitly.

## Event-name convention (snake_case, verb + resource)

- Controllers: `incoming_<verb>_<resource>_request` / `outgoing_<verb>_<resource>_response`.
- Controller error events: `<verb>_<resource>_<reason>` (e.g. `get_user_not_found`, `purchase_reward_insufficient_coins`, `complete_mission_unhandled_error`).
- Adapters: `repo_<method>_called` / `repo_<method>_returned`. Error events: `repo_<reason>` (e.g. `repo_entity_not_found`, `repo_concurrent_user_update`).

The first positional argument to a logger call is always the event name; everything else is a keyword:

```python
logger.info("incoming_create_mission_request", title=body.title)
logger.error(
    "get_user_not_found",
    user_id=str(user_id),
    exc_type=type(e).__name__,
    message=str(e),
)
```

## Field conventions

Controllers:
- Incoming: identifiers (`user_id`, `mission_id`, …), business-meaningful payload fields (`title`, `cost`, …). `request_id`, `method`, `path` come from the middleware.
- Outgoing: `status_code`, plus the resource id created/returned or a `count` for list endpoints.
- Errors: `exc_type`, `message`, plus any identifiers known at that point. Unhandled errors add `exc_info=True`.

Adapters:
- Entry: `repo` (class name), identifiers from the call arguments.
- Return: `repo`, identifiers, `count` for list operations.
- Errors: `repo`, `op`, identifiers.

## PII

Phase 1 logs `username` and `email` at INFO in `create_user_controller`. This is acceptable while the app is not deployed externally. **Before shipping**, move PII fields to DEBUG (or redact). Tracked in `CLAUDE.md` and `docs/tech-debt.md` item #12.

## Out of scope for now

JSON renderer, stdlib `dictConfig`, capturing Uvicorn's loggers, log shipping, distributed tracing. All deferred until the app is deployed externally.
