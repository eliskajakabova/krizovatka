import random


class TrafficGenerator:
    LANES = ["L", "S", "R"]

    def generate(self, traffic_intensity: dict[str, int]) -> list[dict]:
        new_vehicles: list[dict] = []

        for direction, intensity in traffic_intensity.items():
            threshold = max(0, min(100, int(intensity)))
            if random.randint(1, 100) <= threshold:
                new_vehicles.append({
                    "from": direction,
                    "lane": random.choice(self.LANES),
                    "state": "waiting",
                    "wait_time": 0.0,
                })

        return new_vehicles
