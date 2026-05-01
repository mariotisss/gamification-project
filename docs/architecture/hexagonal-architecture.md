# Hexagonal Architecture for Gamification Project

The backend follows Hexagonal Architecture, also known as Ports and Adapters. The goal is to keep business rules independent from frameworks, databases, HTTP APIs, and other external tools.

The architecture is now organized by bounded systems instead of one large `gamification_system` package.

## Core Principles

- Dependencies point inward.
- Domain code does not depend on FastAPI, repositories, databases, or external APIs.
- Application services orchestrate use cases using domain entities and ports.
- Infrastructure implements adapters for the outside world.
- Cross-system dependencies should go through ports or shared domain concepts, not concrete infrastructure.
- Each system owns its domain, application logic, ports, controllers, DTOs, and adapters.

## Current Backend Structure

```text
src/
├── backend/
│   ├── core/pkg/
│   │   ├── user_system/
│   │   │   ├── domain/
│   │   │   │   ├── entities/
│   │   │   │   ├── exceptions/
│   │   │   │   └── ports/
│   │   │   │       ├── driven/
│   │   │   │       └── driving/
│   │   │   ├── application/
│   │   │   │   └── use_cases/
│   │   │   └── infrastructure/
│   │   │       ├── driven/adapters/
│   │   │       └── driving/
│   │   │           ├── api/
│   │   │           └── dtos/
│   │   │
│   │   ├── mission_system/
│   │   │   ├── domain/
│   │   │   ├── application/
│   │   │   └── infrastructure/
│   │   │
│   │   ├── reward_system/
│   │   │   ├── domain/
│   │   │   ├── application/
│   │   │   └── infrastructure/
│   │   │
│   │   └── shared/
│   │       ├── domain/
│   │       ├── application/
│   │       └── infrastructure/
│   │
│   ├── cronjobs/
│   ├── tests/
│   └── main.py
│
└── frontend/
```

## System Boundaries

### `user_system`

Owns user-related behavior and data.

Current examples:

- `User` entity
- `UserRepository` driven port
- `UserUseCases` driving port
- `UserService`
- user controllers and DTOs
- `InMemoryUserRepository`

### `mission_system`

Owns mission-related behavior and data.

Current examples:

- `Mission` entity
- `MissionAlreadyCompletedError`
- `MissionRepository` driven port
- `MissionUseCases` driving port
- `MissionService`
- mission controllers and DTOs
- `InMemoryMissionRepository`

`MissionService` needs user data when completing missions. It depends on the `UserRepository` port, not on user infrastructure directly.

### `reward_system`

Owns reward-related behavior and data.

Current examples:

- `Reward` entity
- `InsufficientCoinsError`
- `RewardRepository` driven port
- `RewardUseCases` driving port
- `RewardService`
- reward controllers and DTOs
- `InMemoryRewardRepository`

`RewardService` needs user data when purchasing rewards. It depends on the `UserRepository` port, not on user infrastructure directly.

### `shared`

Contains concepts that are not owned by a single system or are reused across systems.

Current examples:

- `MissionCompletion`
- `EntityNotFoundError`
- `HealthCheckController`

Shared code should stay small. If a concept clearly belongs to one system, it should live in that system instead of `shared`.

## Layer Responsibilities

### Domain Layer

Path:

```text
<system>/domain/
```

Contains business concepts and interfaces.

Typical contents:

- Entities
- Domain exceptions
- Driven ports, such as repository interfaces
- Driving ports, such as use case interfaces

The domain layer should remain pure Python and should not depend on FastAPI, Pydantic, SQLAlchemy, Redis, Celery, or other infrastructure tools.

### Application Layer

Path:

```text
<system>/application/use_cases/
```

Contains use case services that orchestrate domain behavior.

Application services:

- implement driving ports
- coordinate repositories through driven ports
- raise domain/application exceptions
- avoid HTTP-specific behavior
- avoid database-specific behavior

Example services:

- `UserService`
- `MissionService`
- `RewardService`

### Infrastructure Layer

Path:

```text
<system>/infrastructure/
```

Contains adapters for external interaction.

Current adapter types:

```text
infrastructure/
├── driven/adapters/   # outbound implementations, currently in-memory repositories
└── driving/
    ├── api/           # inbound FastAPI controllers
    └── dtos/          # Pydantic request/response DTOs
```

Infrastructure can depend on application and domain code. Domain and application should not depend on infrastructure.

## Ports

Ports are interfaces that define how layers communicate without depending on implementations.

### Driven Ports

Driven ports are outbound interfaces used by application services to access external resources.

Examples:

- `UserRepository`
- `MissionRepository`
- `RewardRepository`

Current implementations are in-memory adapters, but these can later be replaced by PostgreSQL, Redis, or external API adapters without changing domain logic.

### Driving Ports

Driving ports are inbound use case interfaces exposed by the application.

Examples:

- `UserUseCases`
- `MissionUseCases`
- `RewardUseCases`

Controllers depend on these use case interfaces instead of concrete business details.

## Application Composition

`src/backend/main.py` is currently the composition root.

It is responsible for:

1. Creating driven adapters.
2. Creating application services.
3. Injecting repositories into services.
4. Creating the FastAPI application.
5. Injecting services into controllers.
6. Registering routes.

This keeps dependency wiring explicit and easy to follow during Phase 1.

## Current Dependency Direction

```text
FastAPI Controllers / DTOs
        ↓
Application Use Cases
        ↓
Domain Entities + Ports
        ↑
Driven Adapter Implementations
```

More precisely:

- Controllers call application use cases.
- Application services use domain entities and driven ports.
- Driven adapters implement domain ports.
- `main.py` wires concrete adapters into services and services into controllers.
