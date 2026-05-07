# WordUp

`WordUp` is a prompt-to-build operating system. You give it an idea in plain language, it classifies the build, maps the execution lane, and returns either a build artifact, a finish-line roadmap, or a cookbook editing workspace when the idea is recipe-driven.

## What It Does

- Runs a simple `Input -> Logic -> Automation -> Output` flow
- Classifies broad idea types like apps, games, maps, guides, books, offers, and systems
- Returns grounded build output from user-supplied prompt terms
- Includes a cookbook editor mode with chapter navigation, recipe editing, AI parsing, and HTML export

## Stack

- FastAPI backend
- Single-file HTML/CSS/JS frontend
- Python engine for idea classification and output shaping

## Run Locally

```bash
python -m pip install -r requirements.txt
python -m uvicorn agent_slate_app:app --reload
```

Then open:

- `http://127.0.0.1:8000/wordup`

## App Entrypoint

Production app entrypoint:

```bash
agent_slate_app:app
```

That file currently contains:

```python
from agent_slate.app import app
```

So any ASGI host should point at `agent_slate_app:app`.

## Render Deploy

This app is ready for a simple Render web service deploy.

### Option 1: Use `render.yaml`

This repo includes a starter [render.yaml](./render.yaml).

Render settings:

- Runtime: `Python`
- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn agent_slate_app:app --host 0.0.0.0 --port $PORT`

### Option 2: Manual Render Setup

Create a new Web Service on Render and use:

- Build Command:

```bash
pip install -r requirements.txt
```

- Start Command:

```bash
uvicorn agent_slate_app:app --host 0.0.0.0 --port $PORT
```

### After Deploy

Open:

- `/wordup` for the main app
- `/health` for a simple health check

Notes:

- The frontend is served from the FastAPI app itself.
- No separate frontend build step is required.
- If you later move cookbook parsing or auth server-side, add the needed environment variables in Render.

## Key Files

- `agent_slate/static/index.html` - builder cockpit frontend
- `agent_slate/app.py` - FastAPI routes
- `agent_slate/engine.py` - prompt detection and output construction
- `tests/test_agent_slate.py` - regression coverage

## Test

```bash
pytest tests/test_agent_slate.py
```
