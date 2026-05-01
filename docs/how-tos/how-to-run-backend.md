# How to Run the Backend

This guide explains how to start the FastAPI backend locally.

## Prerequisites

- Python 3.12 or newer
- `pip`
- A terminal opened at the project root

Project root example:

```text
/Users/mario.tiscar/repos/gamification-project
```

## 1. Create the Virtual Environment

From the project root, create the backend virtual environment:

```bash
python3 -m venv src/backend/.venv
```

## 2. Activate the Virtual Environment

```bash
source src/backend/.venv/bin/activate
```

After activation, your shell should show that `.venv` is active.

## 3. Install Dependencies

Install the backend dependencies:

```bash
pip install -r src/backend/requirements.txt
```

## 4. Start the Backend

The simplest option is to run the backend from `src/backend`:

```bash
cd src/backend
uvicorn main:app --host 127.0.0.1 --port 8080 --reload
```

## 5. Check That It Works

Open the health endpoint:

```bash
curl http://127.0.0.1:8080/api/health
```

Expected response:

```json
{"status":"ok"}
```

## 6. Stop the Backend

Press `Ctrl+C` in the terminal running Uvicorn.

## Notes

- The backend currently uses in-memory repositories, so data is lost when the process stops.
- The FastAPI application is defined in `src/backend/main.py`.
- Route registration and dependency wiring are currently handled manually in `main.py`.
