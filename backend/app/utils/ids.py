from uuid import uuid4


def generate_config_id() -> str:
    return f"conf_{uuid4().hex[:8]}"


def generate_simulation_id() -> str:
    return f"sim_{uuid4().hex[:8]}"


def generate_vehicle_id() -> str:
    return f"veh_{uuid4().hex[:8]}"
