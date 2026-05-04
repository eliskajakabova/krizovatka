import asyncio
import json as _json
from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from fastapi import WebSocket

from db.db_config import get_connection
from app.simulation_engine import IntersectionEngine, LAYOUT

# sim_id -> state dict (private keys prefixed with _)
_running: dict[str, dict] = {}

# sim_id -> set of connected WebSocket clients
_ws_clients: dict[str, set[WebSocket]] = {}


async def ws_connect(sim_id: str, ws: WebSocket) -> None:
    """Register a WebSocket client and stream frames until simulation ends."""
    await ws.accept()
    _ws_clients.setdefault(sim_id, set()).add(ws)

    state = _running.get(sim_id)
    if not state:
        await ws.close(code=4004, reason="Simulation not found or already finished")
        return

    # Send setup message immediately
    await ws.send_text(_json.dumps({
        "type":              "setup",
        "simulation_id":     sim_id,
        "config_id":         state["config_id"],
        "cycle_duration":    state["cycle_duration"],
        "signal_timings":    state["signal_timings"],
        "intersection_layout": LAYOUT,
    }))

    try:
        # Keep connection alive — frames are pushed from _broadcast()
        # Ignore any inbound messages (one-directional)
        while True:
            await ws.receive_text()
    except Exception:
        pass
    finally:
        _ws_clients.get(sim_id, set()).discard(ws)


async def _broadcast(sim_id: str, payload: dict) -> None:
    clients = list(_ws_clients.get(sim_id, set()))
    if not clients:
        return
    text = _json.dumps(payload, default=str)
    dead = set()
    for ws in clients:
        try:
            await ws.send_text(text)
        except Exception:
            dead.add(ws)
    for ws in dead:
        _ws_clients.get(sim_id, set()).discard(ws)


def start_simulation(config: dict, req) -> dict:
    sim_id    = f"sim_{uuid4().hex[:8]}"
    now       = datetime.now(timezone.utc)
    intensity = req.traffic_intensity.model_dump()
    timings   = config["signal_timings"]
    cycle     = config["cycle_duration"]

    throughput = {
        d: round(intensity[d] * _green_frac(d, timings, cycle), 1)
        for d in intensity
    }

    state = {
        "simulation_id":       sim_id,
        "config_id":           config["id"],
        "config_name":         config["name"],
        "status":              "running",
        "simulation_duration": req.simulation_duration,
        "traffic_intensity":   intensity,
        "vehicle_speed":       req.vehicle_speed,
        "cycle_duration":      cycle,
        "signal_timings":      timings,
        "started_at":          now,
        "completed_at":        None,
        # live stats (updated by engine)
        "total_vehicles_generated": 0,
        "total_vehicles_passed":    0,
        "average_wait_time":        0.0,
        "max_wait_time":            0.0,
        "intersection_utilization": 0.0,
        "_engine": None,
        "_task":   None,
    }
    _running[sim_id] = state
    _save_to_db(state)

    engine = IntersectionEngine(timings, cycle, req.vehicle_speed, intensity)
    state["_engine"] = engine
    state["_task"]   = asyncio.create_task(_run(sim_id, engine, req.simulation_duration))

    return {
        "simulation_id": sim_id,
        "config_id":     config["id"],
        "config_name":   config["name"],
        "websocket_url": f"ws://localhost:8000/ws/{sim_id}",
        "status":        "running",
        "parameters": {
            "cycle_duration":      cycle,
            "simulation_duration": req.simulation_duration,
            "traffic_intensity":   intensity,
            "vehicle_speed":       req.vehicle_speed,
        },
        "expected_throughput": throughput,
        "started_at":    now,
    }


def get_simulation(sim_id: str) -> dict | None:
    if sim_id in _running:
        return _public(_running[sim_id])
    return _fetch_one(sim_id)


def list_simulations(status: Optional[str], config_id: Optional[str], limit: int) -> list[dict]:
    rows = _fetch_many(status, config_id, limit)
    for row in rows:
        sid = row.get("simulation_id")
        if sid in _running:
            live = _running[sid]
            row["elapsed_time"] = (datetime.now(timezone.utc) - live["started_at"]).total_seconds()
            row["current_statistics"] = {
                "total_vehicles_passed": live["total_vehicles_passed"],
                "average_wait_time":     live["average_wait_time"],
            }
    return rows


def stop_simulation(sim_id: str) -> dict | None:
    state = _running.get(sim_id)
    if not state:
        return None

    if task := state.get("_task"):
        task.cancel()

    state["status"]       = "stopped"
    state["completed_at"] = datetime.now(timezone.utc)
    elapsed = (state["completed_at"] - state["started_at"]).total_seconds()
    engine  = state.get("_engine")
    final   = engine.final_stats() if engine else {}
    _sync_stats(state, final)
    _update_in_db(state)
    _running.pop(sim_id, None)

    return {
        "status":           "stopped",
        "simulation_id":    sim_id,
        "elapsed_time":     round(elapsed, 2),
        "final_statistics": final,
    }


def get_stats(sim_id: str) -> dict | None:
    state = _running.get(sim_id)
    if not state:
        return _fetch_one(sim_id)
    elapsed = (datetime.now(timezone.utc) - state["started_at"]).total_seconds()
    return {
        **_public(state),
        "elapsed_time": round(elapsed, 2),
        "current_statistics": {
            "total_vehicles_passed": state["total_vehicles_passed"],
            "average_wait_time":     state["average_wait_time"],
        },
    }


async def _run(sim_id: str, engine: IntersectionEngine, duration: float):
    state = _running[sim_id]
    try:
        while engine.elapsed < duration:
            frame = engine.step()
            _sync_stats(state, engine.final_stats())
            await _broadcast(sim_id, frame)
            await asyncio.sleep(0.1)

        # Completed
        state["status"]       = "completed"
        state["completed_at"] = datetime.now(timezone.utc)
        final = engine.final_stats()
        _sync_stats(state, final)

        await _broadcast(sim_id, {
            "type":             "completed",
            "total_time":       round(engine.elapsed, 2),
            "final_statistics": final,
        })

    except asyncio.CancelledError:
        pass
    finally:
        _update_in_db(state)
        _running.pop(sim_id, None)
        _ws_clients.pop(sim_id, None)


_DIR_SIGNAL = {"north": "N_S", "south": "S_S", "east": "E_S", "west": "W_S"}


def _green_frac(direction: str, timings: dict, cycle: int) -> float:
    key = _DIR_SIGNAL.get(direction)
    if not key or key not in timings:
        return 0.0
    return timings[key]["duration"] / cycle if cycle else 0.0


def _sync_stats(state: dict, final: dict):
    state["total_vehicles_generated"] = final.get("total_vehicles_generated", state["total_vehicles_generated"])
    state["total_vehicles_passed"]    = final.get("total_vehicles_passed",    state["total_vehicles_passed"])
    state["average_wait_time"]        = final.get("average_wait_time",        state["average_wait_time"])
    state["max_wait_time"]            = final.get("max_wait_time",            state["max_wait_time"])
    state["intersection_utilization"] = final.get("intersection_utilization", state["intersection_utilization"])


def _public(state: dict) -> dict:
    return {k: v for k, v in state.items() if not k.startswith("_")}


def _save_to_db(state: dict) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO simulations
                    (id, config_id, status, simulation_duration,
                     traffic_intensity, vehicle_speed, started_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                state["simulation_id"], state["config_id"], state["status"],
                state["simulation_duration"],
                _json.dumps(state["traffic_intensity"]),
                state["vehicle_speed"], state["started_at"],
            ))
        conn.commit()


def _update_in_db(state: dict) -> None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE simulations SET
                    status                   = %s,
                    completed_at             = %s,
                    total_vehicles_generated = %s,
                    total_vehicles_passed    = %s,
                    average_wait_time        = %s,
                    max_wait_time            = %s,
                    intersection_utilization = %s
                WHERE id = %s
            """, (
                state["status"], state.get("completed_at"),
                state["total_vehicles_generated"], state["total_vehicles_passed"],
                state["average_wait_time"], state["max_wait_time"],
                state["intersection_utilization"], state["simulation_id"],
            ))
        conn.commit()


def _fetch_one(sim_id: str) -> dict | None:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT s.id as simulation_id, s.config_id, c.name as config_name,
                       s.status, s.started_at, s.completed_at,
                       s.total_vehicles_generated, s.total_vehicles_passed,
                       s.average_wait_time, s.max_wait_time, s.intersection_utilization
                FROM simulations s
                LEFT JOIN configurations c ON c.id = s.config_id
                WHERE s.id = %s
            """, (sim_id,))
            row = cur.fetchone()
            if not row:
                return None
            return dict(zip([d[0] for d in cur.description], row))


def _fetch_many(status: Optional[str], config_id: Optional[str], limit: int) -> list[dict]:
    filters, params = [], []
    if status:
        filters.append("s.status = %s"); params.append(status)
    if config_id:
        filters.append("s.config_id = %s"); params.append(config_id)
    where = ("WHERE " + " AND ".join(filters)) if filters else ""
    params.append(limit)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"""
                SELECT s.id as simulation_id, s.config_id, c.name as config_name,
                       s.status, s.started_at, s.completed_at,
                       s.total_vehicles_generated, s.total_vehicles_passed,
                       s.average_wait_time, s.max_wait_time, s.intersection_utilization
                FROM simulations s
                LEFT JOIN configurations c ON c.id = s.config_id
                {where}
                ORDER BY s.started_at DESC LIMIT %s
            """, params)
            cols = [d[0] for d in cur.description]
            return [dict(zip(cols, row)) for row in cur.fetchall()]