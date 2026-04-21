import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from app.api.configurations import router as configurations_router
from app.api.simulations import router as simulations_router
from app.config import API_TITLE, API_VERSION, INTERSECTION_PREFIX
from app.services.configuration_service import ConfigurationService
from app.services.simulation_service import SimulationService
from app.websocket.manager import WebSocketManager

app = FastAPI(title=API_TITLE, version=API_VERSION)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.state.ws_manager = WebSocketManager()
app.state.configuration_service = ConfigurationService()
app.state.simulation_service = SimulationService(
    ws_manager=app.state.ws_manager,
    configuration_service=app.state.configuration_service,
)

app.include_router(configurations_router, prefix=INTERSECTION_PREFIX)
app.include_router(simulations_router, prefix=INTERSECTION_PREFIX)


@app.on_event("startup")
async def on_startup() -> None:
    app.state.ws_manager.set_loop(asyncio.get_running_loop())


@app.get("/")
def root():
    return {"message": "Backend bezi 🚀"}


@app.get("/api/info")
def api_info() -> dict:
    return {
        "name": API_TITLE,
        "version": API_VERSION,
        "api_prefix": INTERSECTION_PREFIX,
        "websocket_pattern": "/ws/{simulation_id}",
    }


@app.websocket("/ws/{simulation_id}")
async def websocket_endpoint(websocket: WebSocket, simulation_id: str):
    ws_manager = app.state.ws_manager
    simulation_service = app.state.simulation_service

    await ws_manager.connect(simulation_id, websocket)

    try:
        simulation = simulation_service.get_simulation(simulation_id)

        if simulation is None:
            await ws_manager.send_personal_message(
                websocket,
                {"type": "error", "message": "Simulation not found"},
            )
            await websocket.close()
            return

        await ws_manager.send_personal_message(
            websocket,
            simulation.build_setup_message(),
        )

        while True:
            await asyncio.sleep(1)

    except WebSocketDisconnect:
        ws_manager.disconnect(simulation_id, websocket)
    except Exception:
        ws_manager.disconnect(simulation_id, websocket)
        await websocket.close()
