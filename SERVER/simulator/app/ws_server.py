import asyncio
import json
import websockets
from app import simulation_service
from app.simulation_engine import LAYOUT

async def handler(websocket):
    try:
        data = await websocket.recv()
        msg = json.loads(data)
        sim_id = msg.get("sim_id", "")

        state = simulation_service._running.get(sim_id)
        if not state:
            await websocket.close(4004, "Simulation not found")
            return

        await websocket.send(json.dumps({
            "type":                "setup",
            "simulation_id":       sim_id,
            "config_id":           state["config_id"],
            "cycle_duration":      state["cycle_duration"],
            "signal_timings":      state["signal_timings"],
            "intersection_layout": LAYOUT,
        }))

        simulation_service._ws_clients.setdefault(sim_id, set()).add(websocket)

        try:
            while True:
                await websocket.recv()
        except Exception:
            pass
        finally:
            simulation_service._ws_clients.get(sim_id, set()).discard(websocket)

    except Exception:
        pass

async def start_ws_server():
    async with websockets.serve(handler, "0.0.0.0", 9002):
        await asyncio.Future()