from __future__ import annotations
import random
from uuid import uuid4

DIRECTIONS = ["north", "south", "east", "west"]
OPPOSITE   = {"north": "south", "south": "north", "east": "west", "west": "east"}

# Intersection geometry (metres)
LAYOUT = {"width": 20, "height": 20, "lane_width": 3}

_SPAWN: dict[str, tuple[float, float]] = {
    "north": (0.0,  -15.0),
    "south": (0.0,   15.0),
    "east":  ( 15.0,  0.0),
    "west":  (-15.0,  0.0),
}
_CROSS: dict[str, tuple[float, float]] = {
    "north": (0.0,  0.0),
    "south": (0.0,  0.0),
    "east":  (0.0,  0.0),
    "west":  (0.0,  0.0),
}
_EXIT: dict[str, tuple[float, float]] = {
    "north": (0.0,   15.0),
    "south": (0.0,  -15.0),
    "east":  (-15.0,  0.0),
    "west":  ( 15.0,  0.0),
}

# Mapovanie from+to na pruh (L/S/R)
_LANE_MAP = {
    "north": {"south": "S", "east": "L", "west": "R"},
    "south": {"north": "S", "west": "L", "east": "R"},
    "east":  {"west": "S", "north": "L", "south": "R"},
    "west":  {"east": "S", "south": "L", "north": "R"},
}

# Mapovanie smer+pruh na kľúč semaforu
_TURN_SIGNALS = {
    "north": {"S": "N_S", "L": "N_L", "R": "N_R"},
    "south": {"S": "S_S", "L": "S_L", "R": "S_R"},
    "east":  {"S": "E_S", "L": "E_L", "R": "E_R"},
    "west":  {"S": "W_S", "L": "W_L", "R": "W_R"},
}


class Vehicle:
    def __init__(self, from_dir: str, to_dir: str):
        self.id       = f"v_{uuid4().hex[:6]}"
        self.from_dir = from_dir
        self.to_dir   = to_dir
        self.x, self.y = _SPAWN[from_dir]
        self.state    = "approaching"   # approaching | waiting | crossing | exited
        self.wait     = 0.0

    def _get_turn(self) -> str:
        return _LANE_MAP.get(self.from_dir, {}).get(self.to_dir, "S")

    def to_dict(self) -> dict:
        return {
            "id":       self.id,
            "from":     self.from_dir,
            "to":       self.to_dir,
            "position": {"x": round(self.x, 2), "y": round(self.y, 2)},
            "state":    self.state,
            "turn":     self._get_turn(),
        }


class IntersectionEngine:
    def __init__(self, signal_timings: dict, cycle: int, speed: float, intensity: dict):
        self.signal_timings = signal_timings
        self.cycle          = cycle
        self.speed          = speed
        self.intensity      = intensity
        self.tick           = 0.1

        self.vehicles:   list[Vehicle] = []
        self.elapsed:    float = 0.0
        self._spawn_acc: dict[str, float] = {d: 0.0 for d in DIRECTIONS}

        self.total_generated = 0
        self.total_passed    = 0
        self.wait_times:     list[float] = []
        self.queue_samples:  list[float] = []

    def step(self) -> dict:
        self.elapsed = round(self.elapsed + self.tick, 3)
        cycle_time   = self.elapsed % self.cycle
        signals      = self._compute_signals(cycle_time)

        self._spawn_vehicles()
        self._move_vehicles(signals)

        active = [v for v in self.vehicles if v.state != "exited"]
        queued = [v for v in active if v.state == "waiting"]
        self.queue_samples.append(len(queued))

        queues = {d: sum(1 for v in queued if v.from_dir == d) for d in DIRECTIONS}

        return {
            "type":       "state",
            "time":       self.elapsed,
            "cycle_time": round(cycle_time, 3),
            "signals":    signals,
            "vehicles":   [v.to_dict() for v in active],
            "queue_lengths": queues,
            "statistics": {
                "total_vehicles_generated": self.total_generated,
                "total_vehicles_passed":    self.total_passed,
                "total_vehicles_waiting":   len(queued),
                "average_wait_time":        round(
                    sum(self.wait_times) / len(self.wait_times), 2
                ) if self.wait_times else 0.0,
            },
        }

    def final_stats(self) -> dict:
        avg_q = round(sum(self.queue_samples) / len(self.queue_samples), 2) if self.queue_samples else 0.0
        max_q = max(self.queue_samples, default=0)
        avg_w = round(sum(self.wait_times) / len(self.wait_times), 2) if self.wait_times else 0.0
        max_w = round(max(self.wait_times, default=0.0), 2)

        total_green = sum(
            self._direction_green_fraction(d) for d in DIRECTIONS
        )
        utilization = round(min(total_green / len(DIRECTIONS), 1.0), 3)

        return {
            "total_vehicles_generated":  self.total_generated,
            "total_vehicles_passed":     self.total_passed,
            "average_wait_time":         avg_w,
            "max_wait_time":             max_w,
            "average_queue_length":      avg_q,
            "max_queue_length":          int(max_q),
            "intersection_utilization":  utilization,
        }

    def _compute_signals(self, cycle_time: float) -> dict[str, str]:
        result = {}
        for key, timing in self.signal_timings.items():
            start = timing["start"]
            end   = start + timing["duration"]
            if timing["duration"] == 0:
                result[key] = "red"
            elif end <= self.cycle:
                result[key] = "green" if start <= cycle_time < end else "red"
            else:
                result[key] = "green" if cycle_time >= start or cycle_time < (end % self.cycle) else "red"
        return result

    def _is_green(self, vehicle: Vehicle, signals: dict) -> bool:
        turn = vehicle._get_turn()
        key  = _TURN_SIGNALS.get(vehicle.from_dir, {}).get(turn)
        return key is not None and signals.get(key) == "green"

    def _spawn_vehicles(self):
        for direction in DIRECTIONS:
            rate = self.intensity.get(direction, 0)
            self._spawn_acc[direction] += rate / 60 * self.tick
            while self._spawn_acc[direction] >= 1.0:
                self._spawn_acc[direction] -= 1.0
                to_dir = random.choice([d for d in DIRECTIONS if d != direction])
                self.vehicles.append(Vehicle(direction, to_dir))
                self.total_generated += 1

    def _move_vehicles(self, signals: dict):
        dist = self.speed * self.tick
        for v in self.vehicles:
            if v.state == "exited":
                continue

            if v.state == "approaching":
                v.x, v.y = self._move_toward(v.x, v.y, 0.0, 0.0, dist)
                if abs(v.x) < 1.5 and abs(v.y) < 1.5:
                    if self._is_green(v, signals):
                        v.state = "crossing"
                    else:
                        v.state = "waiting"

            elif v.state == "waiting":
                v.wait += self.tick
                if self._is_green(v, signals):
                    v.state = "crossing"

            elif v.state == "crossing":
                ex, ey = _EXIT[v.to_dir]
                v.x, v.y = self._move_toward(v.x, v.y, ex, ey, dist)
                if abs(v.x - ex) < 1.0 and abs(v.y - ey) < 1.0:
                    v.state = "exited"
                    self.total_passed += 1
                    if v.wait > 0:
                        self.wait_times.append(v.wait)

        self.vehicles = [v for v in self.vehicles if v.state != "exited"]

    @staticmethod
    def _move_toward(x, y, tx, ty, dist) -> tuple[float, float]:
        dx, dy = tx - x, ty - y
        length = (dx**2 + dy**2) ** 0.5
        if length <= dist:
            return tx, ty
        factor = dist / length
        return x + dx * factor, y + dy * factor

    def _direction_green_fraction(self, direction: str) -> float:
        key = _TURN_SIGNALS.get(direction, {}).get("S")
        if not key or key not in self.signal_timings:
            return 0.0
        return self.signal_timings[key]["duration"] / self.cycle
