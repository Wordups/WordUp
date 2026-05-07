from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from .catalog import AGENT_CATALOG
from .engine import launch_agent_slate
from .models import AgentSlateRequest, AgentSlateResponse


BASE_DIR = Path(__file__).resolve().parent
UI_PATH = BASE_DIR / "static" / "index.html"

app = FastAPI(title="WordUp", version="0.2.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/wordup/catalog")
@app.get("/api/agent-slate/catalog")
def catalog() -> list[dict[str, object]]:
    return [
        {
            "role": blueprint.role,
            "title": blueprint.title,
            "purpose": blueprint.purpose,
            "skills": list(blueprint.skills),
            "tags": list(blueprint.tags),
        }
        for blueprint in AGENT_CATALOG
    ]


@app.post("/api/wordup/launch", response_model=AgentSlateResponse)
@app.post("/api/agent-slate/launch", response_model=AgentSlateResponse)
def launch(request: AgentSlateRequest) -> AgentSlateResponse:
    return launch_agent_slate(request)


@app.get("/", response_class=HTMLResponse)
@app.get("/wordup", response_class=HTMLResponse)
@app.get("/agent-slate", response_class=HTMLResponse)
def index() -> HTMLResponse:
    return HTMLResponse(UI_PATH.read_text(encoding="utf-8"))
