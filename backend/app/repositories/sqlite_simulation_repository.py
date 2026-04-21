from datetime import datetime

from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models.simulation import SimulationModel
from app.engine.intersection_simulation import IntersectionSimulation


class SQLiteSimulationRepository:
    def __init__(self) -> None:
        self._active: dict[str, IntersectionSimulation] = {}

    def _session(self) -> Session:
        return SessionLocal()

    def _parse_datetime(self, value: str | None) -> datetime | None:
        if value is None:
            return None
        return datetime.fromisoformat(value)

    def _to_dict(self, model: SimulationModel) -> dict:
        return {
            "simulation_id": model.id,
            "config_id": model.config_id,
            "status": model.status,
            "simulation_duration": model.simulation_duration,
            "traffic_intensity": model.traffic_intensity,
            "started_at":
            model.started_at.isoformat() if model.started_at else None,
            "completed_at":
            model.completed_at.isoformat() if model.completed_at else None,
            "elapsed_time": model.elapsed_time,
            "statistics": {
                "total_vehicles_generated": model.total_vehicles_generated,
                "total_vehicles_passed": model.total_vehicles_passed,
                "total_vehicles_waiting": model.total_vehicles_waiting,
                "average_wait_time": model.average_wait_time,
                "max_wait_time": model.max_wait_time,
                "average_queue_length": model.average_queue_length,
                "max_queue_length": model.max_queue_length,
                "intersection_utilization": model.intersection_utilization,
            },
        }

    # =========================
    # ACTIVE (RAM)
    # =========================

    def save_active(self,
                    simulation:
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
        db = self._session()
        try:
            model = SimulationModel(
                id=snapshot["simulation_id"],
                config_id=snapshot["config_id"],
                status=snapshot["status"],
                simulation_duration=snapshot["simulation_duration"],
                traffic_intensity=snapshot["traffic_intensity"],
                started_at=self._parse_datetime(snapshot["started_at"]),
                completed_at=self._parse_datetime(snapshot["completed_at"]),
                elapsed_time=snapshot["elapsed_time"],
                total_vehicles_generated=snapshot[
                    "statistics"].get("total_vehicles_generated"),
                total_vehicles_passed=snapshot[
                    "statistics"].get("total_vehicles_passed"),
                total_vehicles_waiting=snapshot[
                    "statistics"].get("total_vehicles_waiting"),
                average_wait_time=snapshot[
                    "statistics"].get("average_wait_time"),
                max_wait_time=snapshot["statistics"].get("max_wait_time"),
                average_queue_length=snapshot[
                    "statistics"].get("average_queue_length"),
                max_queue_length=snapshot[
                    "statistics"].get("max_queue_length"),
                intersection_utilization=snapshot[
                    "statistics"].get("intersection_utilization"),
            )
            db.add(model)
            db.commit()
            db.refresh(model)
            return self._to_dict(model)
        finally:
            db.close()

    def get_finished(self, simulation_id: str) -> dict | None:
        db = self._session()
        try:
            model = db.get(SimulationModel, simulation_id)
            if model is None:
                return None
            return self._to_dict(model)
        finally:
            db.close()

    def list_finished(self) -> list[dict]:
        db = self._session()
        try:
            models = db.query(SimulationModel).all()
            return [self._to_dict(model) for model in models]
        finally:
            db.close()
