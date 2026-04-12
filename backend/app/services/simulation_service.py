import threading
from fastapi import HTTPException

from app.config import SIMULATION_TICK_SECONDS
from app.engine.intersection_simulation import IntersectionSimulation
from app.utils.ids import generate_simulation_id


class SimulationService:
    def __init__(self, ws_manager, configuration_service) -> None:
        self.ws_manager = ws_manager
        self.configuration_service = configuration_service
        self.active_simulations: dict[str, IntersectionSimulation] = {}
        self._lock = threading.Lock()

    def start_simulation(self, payload) -> dict:
        config = self.configuration_service.get_configuration(
            payload.config_id)
        if config is None:
            raise HTTPException(
                status_code=404, detail="Configuration not found")

        simulation_id = generate_simulation_id()

        simulation = IntersectionSimulation(
            simulation_id=simulation_id,
            config_id=payload.config_id,
            cycle_duration=config["cycle_duration"],
            signal_timings=config["signal_timings"],
            simulation_duration=payload.simulation_duration,
            traffic_intensity=payload.traffic_intensity.model_dump(),
            ws_manager=self.ws_manager,
            tick_seconds=SIMULATION_TICK_SECONDS,
            on_finish=self.remove_simulation,
        )

        with self._lock:
            self.active_simulations[simulation_id] = simulation

        simulation.start()

        return {
            "simulation_id": simulation_id,
            "config_id": payload.config_id,
            "websocket_url": f"/ws/{simulation_id}",
            "status": "running",
        }

    def stop_simulation(self, simulation_id: str) -> dict | None:
        simulation = self.get_simulation(simulation_id)
        if simulation is None:
            return None

        simulation.stop()
        simulation.join(timeout=1.0)

        return {
            "status": "stopped",
            "simulation_id": simulation_id,
            "elapsed_time": round(simulation.current_time, 2),
            "final_statistics": simulation.statistics,
        }

    def get_simulation(self, simulation_id: str):
        with self._lock:
            return self.active_simulations.get(simulation_id)

    def get_simulation_response(self, simulation_id: str) -> dict | None:
        simulation = self.get_simulation(simulation_id)
        if simulation is None:
            return None

        return {
            "simulation_id": simulation.simulation_id,
            "config_id": simulation.config_id,
            "status": simulation.status,
            "simulation_duration": simulation.simulation_duration,
            "traffic_intensity": simulation.traffic_intensity,
        }

    def get_simulation_stats(self, simulation_id: str) -> dict | None:
        simulation = self.get_simulation(simulation_id)
        if simulation is None:
            return None

        return {
            "simulation_id": simulation.simulation_id,
            "status": simulation.status,
            "statistics": simulation.statistics,
        }

    def list_simulations(
            self, status:
            str | None = None, config_id: str | None = None) -> dict:
        with self._lock:
            sims = list(self.active_simulations.values())

        result = []
        for sim in sims:
            if status and sim.status != status:
                continue
            if config_id and sim.config_id != config_id:
                continue

            result.append({
                "simulation_id": sim.simulation_id,
                "config_id": sim.config_id,
                "status": sim.status,
            })

        return {"simulations": result}

    def remove_simulation(self, simulation_id: str) -> None:
        with self._lock:
            self.active_simulations.pop(simulation_id, None)
