# Gamification Scratch - Complete Project Summary

This document provides an expanded, detailed overview of the Gamification Scratch project. It aims to explain not just _what_ the project is, but _how_ it works under the hood and its architectural decisions.

## 1. What is this project?

Gamification Scratch is a **developer productivity platform** built to gamify the software development lifecycle. Specifically, it tracks metrics—such as GitHub Copilot usage, lines of code written, and tasks completed—and turns them into a game.

Developers earn **Experience Points (XP)** for their work, unlock **Badges** (achievements), and try to climb the **Leaderboard** against their peers. The goal is to motivate teams and make everyday developer tasks feel rewarding.

## 2. Core Features (The "Gamification Loop")

The platform operates on a very specific loop to engage users:

1. **Missions**: Admins or the system define challenges (e.g., "Use Copilot to generate 500 lines of code this week").
2. **Metrics Gathering**: The backend collects data (from GitHub Copilot telemetry, Snowflake databases, or direct API inputs) to track user progress.
3. **Rewards (Badges & XP)**: Once a mission threshold is crossed, the backend awards XP to the user and unlocks badges on their profile.
4. **Social Competition**: The frontend displays a global Leaderboard, pitting team members against each other based on their accumulated XP.
5. **Notifications**: Users are actively alerted via a notification system in the dashboard whenever they level up, unlock a badge, or complete a mission.

---

## 3. The Tech Stack: Deep Dive

This project relies on a modern, decoupled architecture: a powerful REST API for logic and data storage, and a separate frontend for the interactive user experience.

### Database: PostgreSQL 15

- **Why PostgreSQL?** It provides robust relational data storage. In gamification, transactional integrity is critical (you don't want a user losing XP or gaining a badge twice).
- **Setup:** It runs as its own isolated Docker container (`database` service), with persistent volumes so data isn't lost if the server restarts.

### Backend: Django & Django REST Framework (DRF)

The backend is written in Python using Django 5.2. It acts as the "referee" of the gamification platform.

- **Why Django?** Django's built-in ORM makes it incredibly easy to model complex relationships (Users -> Teams -> Missions -> XP -> Badges). Its built-in admin panel also provides a way to manage the game state easily without writing extra code.
- **REST Framework:** DRF exposes the database as API endpoints (JSON), allowing the frontend to easily fetch leaderboard stats or user profiles.
- **Authentication:** `djangorestframework-simplejwt` provides JSON Web Tokens (JWT). This means the frontend can verify user identity securely without needing to maintain server-side sessions.
- **Testing:** `pytest` and `pytest-django` ensure that core gamification logic (e.g., leveling up) works without bugs before going into production.

**Backend Apps Breakdown:**

- `users`: Extends Django's default user model to add XP fields and handles JWT logins.
- `teams`: Allows grouping users into squads for team-based challenges.
- `missions` & `badges`: The core logic that defines what users need to do and what they get in return.
- `copilot_metrics`: Focuses heavily on GitHub Copilot usage as the primary input mechanism to measure productivity.
- `analytics`: Crunching raw metrics into digestable summaries for the Streamlit dashboard.

### Frontend: Streamlit

The frontend is a data-app built entirely in Python using Streamlit 1.45.

- **Why Streamlit?** Since this project is highly data-driven (displaying metrics, charts, and leaderboards), Streamlit is perfect. It allows Python developers to build rich, reactive user interfaces without having to write raw React/Vue/Angular code.
- **UI & Visualization:** It uses libraries like `Plotly` and `Pandas` to generate interactive line charts showing "Missions completed over time".
- **Communication (`api_client.py`)**: The frontend does not talk to the database directly. Instead, it hits the Django API using the `requests` library, passing the JWT token for secure access.
- **Extensions:** It utilizes `streamlit-option-menu`, `streamlit-card`, and custom CSS to make the dashboard look like a modern gaming panel rather than a standard spreadsheet app.

### Infrastructure: Docker & Docker Compose

- **Why Docker?** It guarantees that the project will run the exact same way on your laptop as it does on a production server.
- **`docker-compose.yml`**: This file is the "conductor". It starts PostgreSQL first, then the Django backend, and finally the Streamlit frontend. It links them together via a virtual container network and maps their ports to your local machine (`8000` for API, `8501` for Dashboard, `5432` for DB).

---

## 4. Development & New Version Considerations

If you are planning to build an improved version, here are the architectural flow patterns to keep in mind:

1. **The Auth Flow**: A user goes to `localhost:8501` (Frontend), types credentials -> Streamlit calls `POST /api/login/` on Backend (`8000`) -> Backend returns a JWT token -> Streamlit stores it in session state.
2. **The Data Flow**: Streamlit needs the Top 10 users -> calls `GET /api/leaderboard/` with the JWT -> Django's `users` app queries PostgreSQL (ordered by XP descending) -> DRF serializes the top 10 users to JSON -> Streamlit renders them in markdown.
3. **Future Scaling**: If the metrics (like Copilot events) start coming in via thousands of events per second, the simple PostgreSQL/Django setup might bottleneck. You would likely need to introduce a message broker like **Redis** + **Celery** to process XP awards asynchronously so the primary API doesn't slow down.
