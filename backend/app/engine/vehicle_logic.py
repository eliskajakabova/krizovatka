from app.utils.ids import generate_vehicle_id


def create_vehicle(direction: str) -> dict:
    return {
        "id": generate_vehicle_id(),
        "from": direction,
        "state": "waiting",
        "wait_time": 0.0,
    }


def update_waiting_vehicles(queues: dict[str, list[dict]],
                            tick_seconds: float) -> None:
    for queue in queues.values():
        for vehicle in queue:
            if vehicle["state"] == "waiting":
                vehicle["wait_time"] += tick_seconds
