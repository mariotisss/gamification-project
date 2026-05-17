# Domain Entities, ORM Models, and DTOs

This document explains why the backend represents the same concept (e.g. a user) with three different classes, and why those classes must stay separate even when their fields overlap.

## 1. The Three Shapes

For every bounded system, the same concept lives in three places:

| Shape           | Location                                                | Purpose                                                  | Technology             |
| --------------- | ------------------------------------------------------- | -------------------------------------------------------- | ---------------------- |
| Domain entity   | `<system>/domain/entities/`                             | Business rules and invariants                            | Pure Python dataclass  |
| ORM model       | `<system>/infrastructure/driven/persistence/models/`    | How the row is stored in PostgreSQL                      | SQLAlchemy 2.0 mapped  |
| HTTP DTOs       | `<system>/infrastructure/driving/dtos/`                 | The wire contract exposed to API clients                 | Pydantic `BaseModel`   |

Example from `user_system`:

- `User` (domain) — owns `add_xp`, `add_dev_coins`, `deduct_dev_coins`, level recalculation.
- `UserModel` (ORM) — carries column types, uniqueness, nullability, FKs, indexes.
- `CreateUserRequest`, `UserResponse` (DTOs) — define the JSON shape accepted from and returned to clients.

## 2. Why They Are Not the Same

Each shape answers a different question and changes for a different reason.

### Domain entity — *what is this concept in our business?*

- Owns behavior (`User.add_xp` mutates `xp` and recomputes `level` together).
- Enforces invariants (cannot deduct more DevCoins than the user has).
- Must remain pure: no SQLAlchemy, no Pydantic, no FastAPI. The hexagon depends on this.

### ORM model — *how is this concept stored?*

- Carries database concerns the domain must not know about: column lengths, uniqueness constraints, FK targets, indexes, relationships, soft-delete flags, `updated_at`, etc.
- Lives in the driven adapter layer. Importing it from the domain would invert the dependency direction.

### HTTP DTOs — *what is the API contract?*

- Shaped for the **client**, not the domain.
- Request DTOs (e.g. `CreateUserRequest`) intentionally omit server-controlled fields like `id`, `xp`, `level`, `created_at`. A client must not be allowed to set those.
- Response DTOs serialize types that have no JSON equivalent: `UUID` becomes `str`, `datetime` becomes an ISO `str`.

## 3. Why They Cannot Be Unified

Merging any two of these shapes breaks down quickly:

1. **Request ≠ response.** A single class either lets clients set protected fields on create, or makes everything optional and loses validation power.
2. **Domain has behavior, DTOs do not.** If `add_xp` lived on the class returned by the controller, business logic would leak into the wire format.
3. **ORM concerns are not domain concerns.** Column lengths, uniqueness, relationships, and indexes belong next to the table definition, not in the entity that expresses business rules.
4. **They change for different reasons.**
   - Domain changes when business rules change.
   - ORM changes when persistence changes (new column, new index, new FK).
   - DTOs change when the API contract changes.
   - Coupling them turns any one of those forces into a breaking change for all callers.
5. **Field types intentionally differ.** Domain uses `UUID` and `datetime`. The DB uses `PgUUID(as_uuid=True)` and `DateTime(timezone=True)`. JSON uses `str`. One class cannot honor all three.

## 4. Where They Meet: Mappers

The shapes are connected by small, explicit mapping functions that live at the boundary that owns the translation:

- **ORM ↔ Domain** — `_to_domain` and `_to_model` helpers inside each Postgres adapter (e.g. `postgres_user_repository.py`). The domain never sees `UserModel`.
- **Domain → DTO** — `build_response(...)` helpers inside each controller (e.g. `get_user_controller.py`). The HTTP layer never returns a domain entity directly.

These mappers are the price of separation. They are intentionally small and local — they exist so the layers can evolve independently.

## 5. Rule of Thumb

- Same fields today, **different reasons to change tomorrow** → keep separate.
- A class imported by two layers is owned by both forever — avoid it in hexagonal code.
- If a shape grows behavior, persistence concerns, or wire-format concerns mixed together, split it before it spreads.

The overlap visible in Phase 1 is a consequence of an early, simple model. As features grow (authentication fields, audit columns, partial list responses, soft deletes, computed fields) the three shapes diverge naturally, and the separation pays for itself.
