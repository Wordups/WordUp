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

## Key Files

- `agent_slate/static/index.html` - builder cockpit frontend
- `agent_slate/app.py` - FastAPI routes
- `agent_slate/engine.py` - prompt detection and output construction
- `tests/test_agent_slate.py` - regression coverage

## Test

```bash
pytest tests/test_agent_slate.py
```
