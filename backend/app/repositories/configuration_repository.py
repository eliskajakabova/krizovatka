class ConfigurationRepository:
    def __init__(self) -> None:
        self._storage: dict[str, dict] = {}

    def save(self, config: dict) -> dict:
        self._storage[config["config_id"]] = config
        return config

    def get_by_id(self, config_id: str) -> dict | None:
        return self._storage.get(config_id)

    def list_all(self) -> list[dict]:
        return list(self._storage.values())

    def delete(self, config_id: str) -> dict | None:
        return self._storage.pop(config_id, None)

    def update(self, config_id: str, config: dict) -> dict:
        self._storage[config_id] = config
        return config
