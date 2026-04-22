from datetime import UTC, datetime
import threading
import time

from app.config import VEHICLE_CROSSING_SECONDS
from app.engine.state_machine import get_signal_states
from app.engine.vehicle_logic import create_vehicle, update_waiting_vehicles
from app.services.statistics_service import StatisticsService
from app.services.traffic_generator import TrafficGenerator


class IntersectionSimulation:
    def __init__(
        self,
        simulation_id: str,
        config_id: str,
        cycle_duration: int,
        signal_timings: dict,
        simulation_duration: int,
        traffic_intensity: dict,
        ws_manager,
        tick_seconds: float = 0.1,
        on_finish=None,
    ) -> None:
        self.simulation_id = simulation_id
        self.config_id = config_id
        self.cycle_duration = cycle_duration
        self.signal_timings = signal_timings
        self.simulation_duration = simulation_duration
        self.traffic_intensity = traffic_intensity
        self.ws_manager = ws_manager
        self.tick_seconds = tick_seconds
        self.on_finish = on_finish

        self.status = "created"
        self.current_time = 0.0
        self.thread: threading.Thread | None = None
        self.stop_event = threading.Event()

        self.started_at = datetime.now(UTC).isoformat()
        self.completed_at: str | None = None

        self.queues: dict[str, dict[str, list[dict]]] = {
            "north": {"L": [], "S": [], "R": []},
            "south": {"L": [], "S": [], "R": []},
            "east": {"L": [], "S": [], "R": []},
            "west": {"L": [], "S": [], "R": []},
        }

        self.crossing_vehicles: list[dict] = []

        self.statistics = StatisticsService.create_initial_statistics()
        self.traffic_generator = TrafficGenerator()

    def start(self) -> None:
        self.status = "running"
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        self.stop_event.set()
        self.status = "stopped"
        if self.completed_at is None:
            self.completed_at = datetime.now(UTC).isoformat()

    def join(self, timeout: float | None = None) -> None:
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=timeout)

    def _run_loop(self) -> None:
        try:
            while (
                self.current_time < self.simulation_duration
                and not self.stop_event.is_set()
            ):
                self._tick()
                time.sleep(self.tick_seconds)
                self.current_time += self.tick_seconds

            if self.status != "stopped":
                self.status = "completed"

            if self.completed_at is None:
                self.completed_at = datetime.now(UTC).isoformat()

            self.ws_manager.broadcast_from_thread(
                self.simulation_id,
                self.build_completed_message(),
            )
        finally:
            if callable(self.on_finish):
                self.on_finish(self.simulation_id)

    def _tick(self) -> None:
        cycle_time = round(self.current_time % self.cycle_duration, 2)

        signals = get_signal_states(
            self.signal_timings,
            cycle_time,
            self.cycle_duration,
        )

        new_vehicles = self.traffic_generator.generate(self.traffic_intensity)

        for vehicle in new_vehicles:
            vehicle_obj = create_vehicle(vehicle["from"], vehicle["lane"])
            self.queues[vehicle["from"]][vehicle["lane"]].append(vehicle_obj)
            self.statistics["total_vehicles_generated"] += 1

        update_waiting_vehicles(self.queues, self.tick_seconds)

        self._update_crossing_vehicles()
        self._process_green_signals(signals)
        self._update_statistics()

        self.ws_manager.broadcast_from_thread(
            self.simulation_id,
            self.build_state_message(signals, cycle_time),
        )

    def _process_green_signals(self, signals: dict[str, str]) -> None:
        signal_to_queue = {
            "N_L": ("north", "L"),
            "N_S": ("north", "S"),
            "N_R": ("north", "R"),
            "S_L": ("south", "L"),
            "S_S": ("south", "S"),
            "S_R": ("south", "R"),
            "E_L": ("east", "L"),
            "E_S": ("east", "S"),
            "E_R": ("east", "R"),
            "W_L": ("west", "L"),
            "W_S": ("west", "S"),
            "W_R": ("west", "R"),
        }

        for signal_id, (direction, lane) in signal_to_queue.items():
            if signals.get(signal_id) != "green":
                continue

            lane_queue = self.queues[direction][lane]
            if not lane_queue:
                continue

            vehicle = lane_queue.pop(0)
            vehicle["state"] = "crossing"
            vehicle["crossing_time_left"] = VEHICLE_CROSSING_SECONDS
            self.crossing_vehicles.append(vehicle)
            self.statistics["total_vehicles_passed"] += 1

    def _update_crossing_vehicles(self) -> None:
        remaining = []

        for vehicle in self.crossing_vehicles:
            vehicle["crossing_time_left"] = round(
                vehicle["crossing_time_left"] - self.tick_seconds,
                2,
            )

            if vehicle["crossing_time_left"] > 0:
                remaining.append(vehicle)

        self.crossing_vehicles = remaining

    def _direction_queue_length(self, direction: str) -> int:
        return sum(len(queue) for queue in self.queues[direction].values())

    def _all_waiting_vehicles(self) -> list[dict]:
        vehicles: list[dict] = []

        for direction_queues in self.queues.values():
            for lane_queue in direction_queues.values():
                vehicles.extend(lane_queue)

        return vehicles

    def _update_statistics(self) -> None:
        queue_lengths = [
            self._direction_queue_length("north"),
            self._direction_queue_length("south"),
            self._direction_queue_length("east"),
            self._direction_queue_length("west"),
        ]
        total_waiting = sum(queue_lengths)

        self.statistics["total_vehicles_waiting"] = total_waiting
        self.statistics["max_queue_length"] = max(
            self.statistics["max_queue_length"],
            max(queue_lengths, default=0),
        )

        if queue_lengths:
            self.statistics["average_queue_length"] = round(
                sum(queue_lengths) / len(queue_lengths),
                2,
            )

        all_wait_times = [
            vehicle["wait_time"] for vehicle in self._all_waiting_vehicles()
        ]

        if all_wait_times:
            self.statistics["average_wait_time"] = round(
                sum(all_wait_times) / len(all_wait_times),
                2,
            )
            self.statistics["max_wait_time"] = round(max(all_wait_times), 2)

        if self.statistics["total_vehicles_generated"] > 0:
            util = (
                self.statistics["total_vehicles_passed"]
                / self.statistics["total_vehicles_generated"]
            )
            self.statistics["intersection_utilization"] = round(util, 3)

    def build_setup_message(self) -> dict:
        return {
            "type": "setup",
            "simulation_id": self.simulation_id,
            "config_id": self.config_id,
            "cycle_duration": self.cycle_duration,
            "signal_timings": self.signal_timings,
        }

    def build_state_message(
        self,
        signals: dict[str, str],
        cycle_time: float,
    ) -> dict:
        vehicles = self._all_waiting_vehicles()

        for vehicle in self.crossing_vehicles:
            v = {k: value for k, value in vehicle.items() if k !=
                 "crossing_time_left"}
            vehicles.append(v)

        return {
            "type": "state",
            "time": round(self.current_time, 2),
            "cycle_time": cycle_time,
            "signals": signals,
            "vehicles": vehicles,
            "queue_lengths": {
                "north": self._direction_queue_length("north"),
                "south": self._direction_queue_length("south"),
                "east": self._direction_queue_length("east"),
                "west": self._direction_queue_length("west"),
            },
            "statistics": self.statistics,
        }

    def build_completed_message(self) -> dict:
        return {
            "type": "completed",
            "total_time": round(self.current_time, 2),
            "final_statistics": self.statistics,
        }

    def to_response_dict(self) -> dict:
        return {
            "simulation_id": self.simulation_id,
            "config_id": self.config_id,
            "status": self.status,
            "simulation_duration": self.simulation_duration,
            "traffic_intensity": self.traffic_intensity,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "elapsed_time": round(self.current_time, 2),
        }

    def to_stats_dict(self) -> dict:
        return {
            "simulation_id": self.simulation_id,
            "status": self.status,
            "statistics": self.statistics,
        }

    def to_finished_snapshot(self) -> dict:
        return {
            "simulation_id": self.simulation_id,
            "config_id": self.config_id,
            "status": self.status,
            "simulation_duration": self.simulation_duration,
            "traffic_intensity": self.traffic_intensity,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "elapsed_time": round(self.current_time, 2),
            "statistics": self.statistics.copy(),
        }
