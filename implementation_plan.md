# Gamification Project - V2 Implementation Plan

This document outlines the proposed structure and architecture for the new iteration of the Gamification Project. It is based on a review of the tech debt and structural limitations found in `C:\repos\gamif-scratch` and subsequent architectural refinements.

## 1. Problem Definition & Tech Debt Identified

The first iteration (`gamif-scratch`) served as a great proof of concept but has several architectural and programming practice limitations:

- **Frontend Limitations (Streamlit):**
  - Streamlit is excellent for data science, but injecting custom CSS/JS for real-time notifications or rich interactions is a hacky workaround.
  - Lack of robust client-side state management.
  - Limited capability for rich animations, responsive layouts, and modern gamified UI components.
- **Backend Tech Debt (Django):**
  - **Fat Views:** Business logic was bleeding into views (e.g., manual JSON construction).
  - **Missing Service/Domain Layer:** No clean separation of concerns. Gamification logic (XP awards, level calculations) should reside in a decoupled service layer.
  - **Synchronous Bottlenecks:** Processing events synchronously in the API will become a major bottleneck at scale.

## 2. Proposed Architecture for V2

We propose a **Modern, Event-Driven, Hexagonal Architecture (Ports & Adapters)** for the backend, alongside a decoupled modern frontend.

### 2.1 Technology Stack

- **Frontend App:** Next.js (React) + TailwindCSS. This will allow for a highly interactive, responsive, and beautiful gamification UI with proper animations and component reusability.
- **Backend API:** FastAPI (Python). FastAPI provides high-performance async capabilities, perfect for handling a large volume of metric events, and uses Pydantic for robust request/response validation.
- **Database:** PostgreSQL (Retained, but accessed via adapters adhering to domain ports).
- **Asynchronous Task Queue:** Celery + Redis for processing metrics, calculating XP, and triggering notifications asynchronously without blocking the mainline API.

### 2.2 Proposed Directory Structure

The backend will strictly follow a Hexagonal Architecture (Ports & Adapters), specifically within the `gamification-system`.

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
│   │   │   └── /use_cases                   # Core application logic orchestration (No workflows)
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

## 3. Implementation Phases

### Phase 1: Backend Foundation & Hexagonal Architecture setup

1. Scaffold the FastAPI backend along with the `domain`, `application`, and `infrastructure` layers.
2. Define the **Domain** entities (e.g., `User`, `Mission`, `Reward`) and abstract ports (e.g., `UserRepository`).
3. Build the **Application Use Cases** to handle core orchestrations like completing a mission and awarding XP.
4. Implement the **Infrastructure Adapters** (SQLAlchemy repositories fulfilling the domain ports) and the driving **REST Controllers** via FastAPI.

### Phase 2: Asynchronous Processing (Event-Driven)

1. Introduce Redis and Celery to the Docker stack.
2. Implement **Infrastructure Adapters** for event dispatching (e.g., `EventDispatcherInfrastructure`).
3. Create use cases and background tasks for processing incoming **Productivity Metrics** (e.g., from direct API inputs or other data lakes).
4. Decouple services entirely by ensuring domains communicate strictly via emitted events.

### Phase 3: Modern Frontend Development

1. Bootstrap the Next.js frontend application.
2. Implement the Design System (Tailwind) following modern UI principles (glassmorphism, dark mode, engaging visual feedback).
3. Build the Dashboard, Leaderboard, and Mission pages.
4. Implement WebSockets or Server-Sent Events (SSE) for real-time notification toasts directly from FastAPI.

## 4. Verification Plan

- **Unit Testing:** Implement `pytest`. The domain layer should be tested in isolation (mocking ports). Application Use cases should be tested with in-memory port injections.
- **Integration Testing:** Test the FastAPI infrastructure endpoints (Controllers) using `TestClient` and testing actual Database Adapters using a test SQL database.
- **Frontend Testing:** Verify fast rendering and responsive layouts in Next.js using component tests and potentially Playwright for E2E gamified user flows.
