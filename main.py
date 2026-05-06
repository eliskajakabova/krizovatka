from contextlib import asynccontextmanager
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Query, WebSocket
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
from fastapi.staticfiles import StaticFiles

from app.models import (
    ConfigurationRequest, ConfigurationResponse,
    SimulationRequest, SimulationStartResponse,
    SimulationStopResponse,
)
from app.conflict import find_conflicts
from app import repository
from app import simulation_service
from db.db_config import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title="Intersection Signal API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "http://localhost:8000",
    ],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_cfg_or_404(cfg_id: str) -> dict:
    cfg = repository.fetch_one(cfg_id)
    if not cfg:
        raise HTTPException(status_code=404, detail={"error": "NOT_FOUND", "id": cfg_id})
    return cfg

def _check_not_preset(cfg: dict) -> None:
    if cfg.get("is_preset"):
        raise HTTPException(status_code=403, detail={
            "error": "FORBIDDEN",
            "message": "Preset configurations cannot be modified or deleted",
        })

def _check_conflicts(signal_timings, cycle_duration) -> None:
    if conflicts := find_conflicts(signal_timings, cycle_duration):
        raise HTTPException(status_code=409, detail={
            "error": "SIGNAL_CONFLICT",
            "message": "Conflicting signals active simultaneously",
            "conflicts": conflicts,
        })



@app.post("/api/intersection/configurations", response_model=ConfigurationResponse, status_code=201)
async def create_configuration(body: ConfigurationRequest):
    _check_conflicts(body.signal_timings, body.cycle_duration)
    record = {
        "id":             f"cfg_{uuid4().hex[:8]}",
        "name":           body.name,
        "description":    body.description,
        "cycle_duration": body.cycle_duration,
        "signal_timings": {k: v.model_dump() for k, v in body.signal_timings.items()},
    }
    repository.save_configuration(record)
    return repository.fetch_one(record["id"])


@app.get("/api/intersection/configurations")
async def list_configurations():
    return repository.fetch_all()


@app.get("/api/intersection/configurations/{cfg_id}", response_model=ConfigurationResponse)
async def get_configuration(cfg_id: str):
    return _get_cfg_or_404(cfg_id)


@app.put("/api/intersection/configurations/{cfg_id}", response_model=ConfigurationResponse)
async def update_configuration(cfg_id: str, body: ConfigurationRequest):
    cfg = _get_cfg_or_404(cfg_id)
    _check_not_preset(cfg)
    _check_conflicts(body.signal_timings, body.cycle_duration)
    return repository.update_configuration(cfg_id, {
        "name":           body.name,
        "description":    body.description,
        "cycle_duration": body.cycle_duration,
        "signal_timings": {k: v.model_dump() for k, v in body.signal_timings.items()},
    })


@app.delete("/api/intersection/configurations/{cfg_id}", status_code=204)
async def delete_configuration(cfg_id: str):
    _check_not_preset(_get_cfg_or_404(cfg_id))
    repository.delete_configuration(cfg_id)


@app.get("/api/intersection/configurations/{cfg_id}/history")
async def configuration_history(cfg_id: str):
    _get_cfg_or_404(cfg_id)
    return {"simulations": simulation_service.list_simulations(None, cfg_id, 100)}


@app.get("/api/intersection/presets")
async def list_presets():
    return [c for c in repository.fetch_all() if c.get("is_preset")]



@app.post("/api/intersection/simulations/start", response_model=SimulationStartResponse, status_code=201)
async def start_simulation(body: SimulationRequest):
    cfg = _get_cfg_or_404(body.config_id)
    return simulation_service.start_simulation(cfg, body)


@app.get("/api/intersection/simulations")
async def list_simulations(
    status:    Optional[str] = Query(None, description="running | completed | stopped"),
    config_id: Optional[str] = Query(None),
    limit:     int           = Query(50, ge=1, le=500),
):
    return {"simulations": simulation_service.list_simulations(status, config_id, limit)}


@app.get("/api/intersection/simulations/{sim_id}")
async def get_simulation(sim_id: str):
    sim = simulation_service.get_simulation(sim_id)
    if not sim:
        raise HTTPException(status_code=404, detail={"error": "NOT_FOUND", "id": sim_id})
    return sim


@app.get("/api/intersection/simulations/{sim_id}/stats")
async def get_simulation_stats(sim_id: str):
    stats = simulation_service.get_stats(sim_id)
    if not stats:
        raise HTTPException(status_code=404, detail={"error": "NOT_FOUND", "id": sim_id})
    return stats


@app.delete("/api/intersection/simulations/{sim_id}", response_model=SimulationStopResponse)
async def stop_simulation(sim_id: str):
    result = simulation_service.stop_simulation(sim_id)
    if not result:
        raise HTTPException(status_code=404, detail={"error": "NOT_FOUND", "id": sim_id})
    return result



@app.websocket("/ws/{sim_id}")
async def websocket_endpoint(websocket: WebSocket, sim_id: str):
    await simulation_service.ws_connect(sim_id, websocket)



@app.get("/api/info")
async def server_info():
    return {
        "name":    "Intersection Signal API",
        "version": "1.0.0",
        "endpoints": {
            "configurations": "/api/intersection/configurations",
            "simulations":    "/api/intersection/simulations",
            "presets":        "/api/intersection/presets",
            "websocket":      "ws://localhost:8000/ws/{sim_id}",
            "docs":           "/docs",
        },
    }


@app.exception_handler(RequestValidationError)
async def on_validation_error(request, exc: RequestValidationError):
    errors = exc.errors()
    first  = errors[0]
    loc    = first.get("loc", [])
    field  = ".".join(str(p) for p in loc[1:]) or "unknown"
    return JSONResponse(status_code=400, content={
        "error":   "VALIDATION_FAILED",
        "message": first.get("msg"),
        "field":   field,
    })

# úplne na koniec main.py, po exception_handler
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")