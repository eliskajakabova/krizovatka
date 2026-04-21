from datetime import datetime

from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models.configuration import ConfigurationModel


class SQLiteConfigurationRepository:
    def __init__(self) -> None:
        pass

    def _session(self) -> Session:
        return SessionLocal()

    def _to_dict(self, model: ConfigurationModel) -> dict:
        return {
            "config_id": model.id,
            "name": model.name,
            "description": model.description,
            "cycle_duration": model.cycle_duration,
            "signal_timings": model.signal_timings,
            "is_preset": model.is_preset,
            "cycle_utilization": model.cycle_utilization,
            "times_simulated": model.times_simulated,
            "created_at":
            model.created_at.isoformat() if model.created_at else None,
            "updated_at":
            model.updated_at.isoformat() if model.updated_at else None,
        }

    def _parse_datetime(self, value: str | None) -> datetime | None:
        if value is None:
            return None
        return datetime.fromisoformat(value)

    def save(self, config: dict) -> dict:
        db = self._session()
        try:
            model = ConfigurationModel(
                id=config["config_id"],
                name=config["name"],
                description=config.get("description"),
                cycle_duration=config["cycle_duration"],
                signal_timings=config["signal_timings"],
                is_preset=config.get("is_preset", False),
                cycle_utilization=config.get("cycle_utilization"),
                times_simulated=config.get("times_simulated", 0),
                created_at=self._parse_datetime(config["created_at"]),
                updated_at=self._parse_datetime(config["updated_at"]),
            )
            db.add(model)
            db.commit()
            db.refresh(model)
            return self._to_dict(model)
        finally:
            db.close()

    def get_by_id(self, config_id: str) -> dict | None:
        db = self._session()
        try:
            model = db.get(ConfigurationModel, config_id)
            if model is None:
                return None
            return self._to_dict(model)
        finally:
            db.close()

    def list_all(self) -> list[dict]:
        db = self._session()
        try:
            models = db.query(ConfigurationModel).all()
            return [self._to_dict(model) for model in models]
        finally:
            db.close()

    def delete(self, config_id: str) -> dict | None:
        db = self._session()
        try:
            model = db.get(ConfigurationModel, config_id)
            if model is None:
                return None

            data = self._to_dict(model)
            db.delete(model)
            db.commit()
            return data
        finally:
            db.close()

    def update(self, config_id: str, config: dict) -> dict:
        db = self._session()
        try:
            model = db.get(ConfigurationModel, config_id)
            if model is None:
                raise ValueError(f"Configuration {config_id} not found")

            model.name = config["name"]
            model.description = config.get("description")
            model.cycle_duration = config["cycle_duration"]
            model.signal_timings = config["signal_timings"]
            model.is_preset = config.get("is_preset", False)
            model.cycle_utilization = config.get("cycle_utilization")
            model.times_simulated = config.get("times_simulated", 0)
            model.created_at = self._parse_datetime(config["created_at"])
            model.updated_at = self._parse_datetime(config["updated_at"])

            db.commit()
            db.refresh(model)
            return self._to_dict(model)
        finally:
            db.close()
