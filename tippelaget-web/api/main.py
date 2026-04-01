from __future__ import annotations

import datetime
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from assistants_logic import run_king, run_prophet
from chart_compute import compute_all_dashboard
from cognite_data import (
    build_client,
    check_last_workflow_runtime,
    check_workflow_status,
    create_monthly_innskudd_df,
    execute_workflow,
    get_prepared_bets,
    get_todays_events_prepared,
)
from settings import Settings, get_settings

app = FastAPI(title="Tippelaget Web API", version="0.1.0")


def _cors_allow_origins(settings: Settings) -> list[str]:
    base = [
        "http://127.0.0.1:5173",
        "http://localhost:5173",
        "http://127.0.0.1:4173",
        "http://localhost:4173",
    ]
    extra = [o.strip() for o in settings.cors_extra_origins.split(",") if o.strip()]
    return list(dict.fromkeys(base + extra))


_cors_settings = get_settings()
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_allow_origins(_cors_settings),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ProphetBody(BaseModel):
    question: str = Field(..., min_length=1)


class KingBody(BaseModel):
    question: str = Field(..., min_length=1)
    player: str = Field(..., pattern="^(Elias|Mads|Tobias)$")


@app.get("/api/health")
def health():
    return {"ok": True}


@app.get("/api/dashboard")
def dashboard():
    settings = get_settings()
    client = build_client(settings)
    df = get_prepared_bets(client, settings)
    innskudd = create_monthly_innskudd_df()
    return compute_all_dashboard(df, innskudd)


@app.get("/api/events/today")
def events_today():
    settings = get_settings()
    client = build_client(settings)
    ev = get_todays_events_prepared(client, settings)
    if ev.empty:
        return {"rows": []}
    return {"rows": ev.replace({float("nan"): None}).to_dict(orient="records")}


@app.get("/api/workflow/last-run")
def workflow_last_run():
    settings = get_settings()
    client = build_client(settings)
    ts = check_last_workflow_runtime(client, settings)
    if ts is None:
        return {"created_time_ms": None, "display_utc_plus_2": None}
    try:
        dt = datetime.datetime.fromtimestamp(int(ts) / 1000) + datetime.timedelta(hours=2)
        display = dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, OverflowError, OSError):
        display = None
    return {"created_time_ms": ts, "display_utc_plus_2": display}


@app.post("/api/workflow/run")
def workflow_run():
    settings = get_settings()
    client = build_client(settings)
    res = execute_workflow(client, settings)
    return {"execution_id": res.id}


@app.get("/api/workflow/status/{execution_id}")
def workflow_status(execution_id: int):
    settings = get_settings()
    client = build_client(settings)
    status = check_workflow_status(client, execution_id)
    return {"status": status}


@app.post("/api/assistants/prophet")
def assistant_prophet(body: ProphetBody):
    settings = get_settings()
    client = build_client(settings)
    df = get_prepared_bets(client, settings)
    try:
        answer = run_prophet(df, body.question.strip(), settings)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
    return {"answer": answer}


@app.post("/api/assistants/king")
def assistant_king(body: KingBody):
    settings = get_settings()
    client = build_client(settings)
    df = get_prepared_bets(client, settings)
    ev = get_todays_events_prepared(client, settings)
    try:
        answer = run_king(df, ev, body.question.strip(), body.player, settings)
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e)) from e
    return {"answer": answer}


@app.get("/api/player-image/{name}")
def player_image(name: str):
    settings = get_settings()
    root = Path(settings.repo_root).resolve()
    path = root / f"{name.lower()}.png"
    if not path.is_file():
        raise HTTPException(status_code=404)
    return FileResponse(path, media_type="image/png")


def main():
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
