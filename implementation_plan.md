# Gamification Project - V2 Implementation Plan

This document outlines the proposed structure and architecture for the new iteration of the Gamification Project. It is based on a review of the tech debt and structural limitations found in `C:\repos\gamif-scratch`.

## 1. Problem Definition & Tech Debt Identified

The first iteration (`gamif-scratch`) served as a great proof of concept but has several architectural and programming practice limitations:

- **Frontend Limitations (Streamlit):**
  - Streamlit is excellent for data science, but injecting custom CSS/JS for real-time notifications or rich interactions is a hacky workaround.
  - Lack of robust client-side state management.
  - Limited capability for rich animations, responsive layouts, and modern gamified UI components.
- **Backend Tech Debt (Django):**
  - **Fat Views:** Business logic was bleeding into views (e.g., manual JSON construction).
  - **Missing Service Layer:** No clean separation of concerns. Gamification logic (XP awards, level calculations) should reside in a decoupled service layer.
  - **Synchronous Bottlenecks:** Processing events synchronously in the API will become a major bottleneck at scale.

## 2. Proposed Architecture for V2

We propose a **Modern, Decoupled, and Event-Driven Architecture**.

### 2.1 Technology Stack

- **Frontend App:** Next.js (React) + TailwindCSS. This will allow for a highly interactive, responsive, and beautiful gamification UI with proper animations and component reusability.
- **Backend API:** FastAPI (Python). FastAPI provides high-performance async capabilities, perfect for handling a large volume of metric events, and uses Pydantic for robust request/response validation.
- **Database:** PostgreSQL (Retained, but with an optimized schema using SQLAlchemy/Alembic).
- **Asynchronous Task Queue:** Celery + Redis for processing metrics, calculating XP, and triggering notifications asynchronously without blocking the mainline API.

### 2.2 Proposed Directory Structure

```text
/gamification-v2
│
├── /frontend               # Next.js React Project
│   ├── /components         # Reusable UI components (Buttons, Cards, Badges)
│   ├── /app                # Next.js App Router pages (Dashboard, Leaderboard, Profile)
│   ├── /hooks              # Custom React hooks (e.g., useUser, useLeaderboard)
│   ├── /services           # API integration (Axios/Fetch wrappers)
│   └── /store              # Global State (Zustand or Redux)
│
├── /backend                # FastAPI Backend
│   ├── /api                # API Routers / Controllers (Thin layer)
│   ├── /core               # Configuration, Security, JWT Auth setup
│   ├── /models             # SQLAlchemy Database Models
│   ├── /schemas            # Pydantic Schemas for validation
│   ├── /services           # BUSINESS LOGIC (XP calculation, Badge awards)
│   ├── /tasks              # Celery background tasks
│   └── /tests              # Pytest suite
│
├── /infrastructure         # DevOps, Docker, CI/CD
│   ├── docker-compose.yml
│   └── /scripts            # Database backup/restore scripts
│
└── README.md
```

## 3. Implementation Phases

### Phase 1: Backend Foundation & Service Layer

1. Scaffold the FastAPI backend with SQLAlchemy and Alembic.
2. Implement **Users** and **Auth** (JWT).
3. Build the **Service Layer** to handle XP addition, leveling up, and badge awarding cleanly.
4. Set up Pydantic schemas for clear, validated JSON contracts with the frontend.

### Phase 2: Asynchronous Processing

1. Introduce Redis and Celery to the Docker stack.
2. Create background tasks for processing incoming **Productivity Metrics** (e.g., from direct API inputs or other data lakes).
3. Create an event-driven notification generation system (so API endpoints return instantly while XP is calculated in the background).

### Phase 3: Modern Frontend Development

1. Bootstrap the Next.js frontend application.
2. Implement the Design System (Tailwind) following modern UI principles (glassmorphism, dark mode, engaging visual feedback).
3. Build the Dashboard, Leaderboard, and Mission pages.
4. Implement WebSockets or Server-Sent Events (SSE) for real-time notification toasts directly from FastAPI.

## 4. Verification Plan

- **Unit Testing:** Implement `pytest` for all core gamification services (e.g., `test_xp_calculation.py`, `test_badge_awarded_on_threshold.py`) decoupled from the API layer.
- **Integration Testing:** Test the FastAPI endpoints using `TestClient` to ensure correct serialization and HTTP status codes.
- **Frontend Testing:** Verify fast rendering and responsive layouts in Next.js using component tests and potentially Playwright for E2E gamified user flows.
