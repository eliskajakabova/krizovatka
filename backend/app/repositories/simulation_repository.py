from app.engine.intersection_simulation import IntersectionSimulation


class SimulationRepository:
    def __init__(self) -> None:
        self._active: dict[str, IntersectionSimulation] = {}
        self._finished: dict[str, dict] = {}

    def save_active(
            self, simulation:
            IntersectionSimulation) -> IntersectionSimulation:
        self._active[simulation.simulation_id] = simulation
        return simulation

    def get_active(self, simulation_id: str) -> IntersectionSimulation | None:
        return self._active.get(simulation_id)

    def list_active(self) -> list[IntersectionSimulation]:
        return list(self._active.values())

    def remove_active(
            self, simulation_id: str) -> IntersectionSimulation | None:
        return self._active.pop(simulation_id, None)

    def save_finished(self, snapshot: dict) -> dict:
        self._finished[snapshot["simulation_id"]] = snapshot
        return snapshot

    def get_finished(self, simulation_id: str) -> dict | None:
        return self._finished.get(simulation_id)

    def list_finished(self) -> list[dict]:
        return list(self._finished.values())
