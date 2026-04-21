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
        self.finished_simulations: dict[str, dict] = {}
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
            "config_name": config["name"],
            "websocket_url": f"/ws/{simulation_id}",
            "status": "running",
            "parameters": {
                "cycle_duration": config["cycle_duration"],
                "simulation_duration": payload.simulation_duration,
                "traffic_intensity": payload.traffic_intensity.model_dump(),
            },
            "started_at": simulation.started_at,
        }

    def stop_simulation(self, simulation_id: str) -> dict | None:
        simulation = self.get_simulation(simulation_id)
        if simulation is None:
            return None

        simulation.stop()
        simulation.join(timeout=1.0)

        finished = self._get_finished_simulation(simulation_id)
        if finished is not None:
            return {
                "status": finished["status"],
                "simulation_id": finished["simulation_id"],
                "elapsed_time": finished["elapsed_time"],
                "final_statistics": finished["statistics"],
            }

        return {
            "status": "stopped",
            "simulation_id": simulation_id,
            "elapsed_time": round(simulation.current_time, 2),
            "final_statistics": simulation.statistics,
        }

    def get_simulation(
            self, simulation_id: str) -> IntersectionSimulation | None:
        with self._lock:
            return self.active_simulations.get(simulation_id)

    def _get_finished_simulation(self, simulation_id: str) -> dict | None:
        with self._lock:
            return self.finished_simulations.get(simulation_id)

    def get_simulation_response(self, simulation_id: str) -> dict | None:
        simulation = self.get_simulation(simulation_id)
        if simulation is not None:
            return {
                "simulation_id": simulation.simulation_id,
                "config_id": simulation.config_id,
                "status": simulation.status,
                "simulation_duration": simulation.simulation_duration,
                "traffic_intensity": simulation.traffic_intensity,
                "started_at": simulation.started_at,
                "completed_at": simulation.completed_at,
                "elapsed_time": round(simulation.current_time, 2),
            }

        finished = self._get_finished_simulation(simulation_id)
        if finished is not None:
            return {
                "simulation_id": finished["simulation_id"],
                "config_id": finished["config_id"],
                "status": finished["status"],
                "simulation_duration": finished["simulation_duration"],
                "traffic_intensity": finished["traffic_intensity"],
                "started_at": finished["started_at"],
                "completed_at": finished["completed_at"],
                "elapsed_time": finished["elapsed_time"],
            }

        return None

    def get_simulation_stats(self, simulation_id: str) -> dict | None:
        simulation = self.get_simulation(simulation_id)
        if simulation is not None:
            return {
                "simulation_id": simulation.simulation_id,
                "status": simulation.status,
                "statistics": simulation.statistics,
            }

        finished = self._get_finished_simulation(simulation_id)
        if finished is not None:
            return {
                "simulation_id": finished["simulation_id"],
                "status": finished["status"],
                "statistics": finished["statistics"],
            }

        return None

    def list_simulations(
        self,
        status: str | None = None,
        config_id: str | None = None,
    ) -> dict:
        with self._lock:
            active = list(self.active_simulations.values())
            finished = list(self.finished_simulations.values())

        result = []

        for sim in active:
            if status and sim.status != status:
                continue
            if config_id and sim.config_id != config_id:
                continue

            config = self.configuration_service.get_configuration(
                sim.config_id)
            config_name = config["name"] if config else None

            result.append(
                {
                    "simulation_id": sim.simulation_id,
                    "config_id": sim.config_id,
                    "config_name": config_name,
                    "status": sim.status,
                    "started_at": sim.started_at,
                    "elapsed_time": round(sim.current_time, 2),
                    "current_statistics": sim.statistics,
                }
            )

        for sim in finished:
            if status and sim["status"] != status:
                continue
            if config_id and sim["config_id"] != config_id:
                continue

            config = self.configuration_service.get_configuration(
                sim["config_id"])
            config_name = config["name"] if config else None

            result.append(
                {
                    "simulation_id": sim["simulation_id"],
                    "config_id": sim["config_id"],
                    "config_name": config_name,
                    "status": sim["status"],
                    "started_at": sim["started_at"],
                    "elapsed_time": sim["elapsed_time"],
                    "current_statistics": sim["statistics"],
                }
            )

        return {"simulations": result}

    def _build_finished_snapshot(
            self, simulation: IntersectionSimulation) -> dict:
        return {
            "simulation_id": simulation.simulation_id,
            "config_id": simulation.config_id,
            "status": simulation.status,
            "simulation_duration": simulation.simulation_duration,
            "traffic_intensity": simulation.traffic_intensity,
            "started_at": simulation.started_at,
            "completed_at": simulation.completed_at,
            "elapsed_time": round(simulation.current_time, 2),
            "statistics": simulation.statistics.copy(),
        }

    def remove_simulation(self, simulation_id: str) -> None:
        with self._lock:
            simulation = self.active_simulations.get(simulation_id)
            if simulation is None:
                return

            self.finished_simulations[
                simulation_id] = self._build_finished_snapshot(
                simulation
            )
            self.active_simulations.pop(simulation_id, None)
