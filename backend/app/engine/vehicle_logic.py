from app.utils.ids import generate_vehicle_id


def create_vehicle(direction: str, lane: str) -> dict:
    return {
        "id": generate_vehicle_id(),
        "from": direction,
        "lane": lane,
        "state": "waiting",
        "wait_time": 0.0,
    }


def update_waiting_vehicles(
    queues: dict[str, dict[str, list[dict]]],
    tick_seconds: float,
) -> None:
    for direction_queues in queues.values():
        for lane_queue in direction_queues.values():
            for vehicle in lane_queue:
                if vehicle["state"] == "waiting":
                    vehicle["wait_time"] = round(
                        vehicle["wait_time"] + tick_seconds,
                        2,
                    )
