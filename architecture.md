# Hexagonal Architecture for Gamification Project

- The architecture is modular, separating the frontend from the backend, and centralizing shared utilities.
- The **Backend Gamification System** follows a strict **Hexagonal Architecture (Ports & Adapters)** pattern to strictly decouple core business logic from external dependencies (DBs, APIs).
- Dependencies MUST point inward. 

```text
src/
├── /backend                                 # Backend microservices and cron jobs
│   ├── /core/pkg/gamification-system        # Main Hexagonal Module
│   │   ├── /domain                          # Pure Python (Zero external dependencies)
│   │   │   ├── /entities                    # Business data models + validation
│   │   │   └── /ports                       # Abstract interfaces
│   │   │       ├── /driven                  # Outbound interfaces (e.g., UserRepository)
│   │   │       └── /driving                 # Inbound interfaces (e.g., Use Case definitions)
│   │   │
│   │   ├── /application                     # Application Layer (Depends on Domain)
│   │   │   └── /use_cases                   # Core application logic orchestration
│   │   │
│   │   └── /infrastructure                  # External I/O (Depends on Domain & Application)
│   │       ├── /driven                      # Outbound implementations (e.g., Postgres DB adapters)
│   │       └── /driving                     # Inbound calls (e.g., FastAPI REST routers/controllers)
│   │
│   ├── /cronjobs                            # Scheduled jobs
│   ├── /tests                               # Pytest suite
│   └── /main.py                             # Dependency Injection & Application wiring
│
├── /frontend                                # Next.js React Project
│   ├── /components                          # Reusable UI components
│   ├── /app                                 # Next.js App Router pages
│   ├── /hooks                               # Custom React hooks
│   ├── /services                            # API integration
│   └── /store                               # Global State (Zustand)
│
├── /shared                                  # Shared types across frontend/backend
│
└── /app                                     # Main entry point of the project
```