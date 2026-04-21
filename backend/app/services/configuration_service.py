from datetime import UTC, datetime

from fastapi import HTTPException

from app.services.validation_service import ValidationService
from app.utils.ids import generate_config_id


class ConfigurationService:
    def __init__(self) -> None:
        self.validation_service = ValidationService()
        self._storage: dict[str, dict] = {}
        self._seed_default_configuration()

    def _now_iso(self) -> str:
        return datetime.now(UTC).isoformat()

    def _seed_default_configuration(self) -> None:
        config_id = "conf_default01"

        signal_timings = {
            "N_S": {"start": 0, "duration": 50},
            "N_L": {"start": 50, "duration": 10},
            "N_R": {"start": 0, "duration": 50},
            "S_S": {"start": 0, "duration": 50},
            "S_L": {"start": 50, "duration": 10},
            "S_R": {"start": 0, "duration": 50},
            "E_S": {"start": 60, "duration": 50},
            "E_L": {"start": 110, "duration": 10},
            "E_R": {"start": 60, "duration": 50},
            "W_S": {"start": 60, "duration": 50},
            "W_L": {"start": 110, "duration": 10},
            "W_R": {"start": 60, "duration": 50},
        }

        validation = self.validation_service.validate(120, signal_timings)
        now = self._now_iso()

        self._storage[config_id] = {
            "config_id": config_id,
            "name": "Predvolená konfigurácia",
            "description": "Základná ukážková konfigurácia",
            "cycle_duration": 120,
            "signal_timings": signal_timings,
            "is_preset": True,
            "cycle_utilization": validation["cycle_utilization"],
            "created_at": now,
            "updated_at": now,
            "times_simulated": 0,
        }

    def create_configuration(self, payload) -> dict:
        validation = self.validate_configuration(payload)
        if not validation["valid"]:
            raise HTTPException(status_code=409, detail=validation)

        config_id = generate_config_id()
        now = self._now_iso()

        config = {
            "config_id": config_id,
            "name": payload.name,
            "description": payload.description,
            "cycle_duration": payload.cycle_duration,
            "signal_timings": {
                k: v.model_dump() for k, v in payload.signal_timings.items()
            },
            "is_preset": False,
            "cycle_utilization": validation["cycle_utilization"],
            "created_at": now,
            "updated_at": now,
            "times_simulated": 0,
        }

        self._storage[config_id] = config
        return config

    def list_configurations(self, include_presets: bool = True) -> dict:
        values = list(self._storage.values())

        if not include_presets:
            values = [item for item in values if not item["is_preset"]]

        return {"configurations": values}

    def get_configuration(self, config_id: str) -> dict | None:
        return self._storage.get(config_id)

    def update_configuration(self, config_id: str, payload) -> dict | None:
        config = self._storage.get(config_id)
        if config is None:
            return None

        if config.get("is_preset"):
            raise HTTPException(
                status_code=409,
                detail="Preset configuration cannot be modified",
            )

        candidate = {**config, **payload.model_dump(exclude_none=True)}

        if "signal_timings" in candidate:
            candidate["signal_timings"] = {
                k: (v.model_dump() if hasattr(v, "model_dump") else v)
                for k, v in candidate["signal_timings"].items()
            }

        validation = self.validation_service.validate(
            candidate["cycle_duration"],
            candidate["signal_timings"],
        )

        if not validation["valid"]:
            raise HTTPException(status_code=409, detail=validation)

        candidate["cycle_utilization"] = validation["cycle_utilization"]
        candidate["updated_at"] = self._now_iso()
        self._storage[config_id] = candidate
        return candidate

    def delete_configuration(self, config_id: str) -> dict | None:
        config = self._storage.get(config_id)

        if config and config.get("is_preset"):
            raise HTTPException(
                status_code=409,
                detail="Preset configuration cannot be deleted",
            )

        return self._storage.pop(config_id, None)

    def validate_configuration(self, payload) -> dict:
        signal_timings = {
            key: value.model_dump() if hasattr(value, "model_dump") else value
            for key, value in payload.signal_timings.items()
        }

        return self.validation_service.validate(
            payload.cycle_duration,
            signal_timings,
        )

    def increment_times_simulated(self, config_id: str) -> None:
        config = self._storage.get(config_id)
        if config is None:
            return

        config["times_simulated"] = config.get("times_simulated", 0) + 1
        config["updated_at"] = self._now_iso()
