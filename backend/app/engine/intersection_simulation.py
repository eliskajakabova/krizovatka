import threading
import time
import random 

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

        self.queues: dict[str, list[dict]] = {
            "north": [],
            "south": [],
            "east": [],
            "west": [],
        }

        self.statistics = StatisticsService.create_initial_statistics()
        self.traffic_generator = TrafficGenerator()

    def start(self) -> None:
        self.status = "running"
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()

    def stop(self) -> None:
        self.stop_event.set()
        self.status = "stopped"

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

        # 1. OPRAVA: Najprv vypustíme autá, čo majú zelenú (aby nezmizli z UI)
        self._process_green_signals(signals)

        # 2. Až potom generujeme nové
        new_vehicles = self.traffic_generator.generate(self.traffic_intensity)

        import random # Nezabudnite importovať random!
        for vehicle in new_vehicles:
            vehicle_obj = create_vehicle(vehicle["from"])
            # OPRAVA: Pridelíme autu konkrétny pruh
            vehicle_obj["lane"] = random.choice(["S", "L", "R"])
            self.queues[vehicle["from"]].append(vehicle_obj)
            self.statistics["total_vehicles_generated"] += 1

        update_waiting_vehicles(self.queues, self.tick_seconds)
        self._update_statistics()

        self.ws_manager.broadcast_from_thread(
            self.simulation_id,
            self.build_state_message(signals, cycle_time),
        )

    def _process_green_signals(self, signals: dict[str, str]) -> None:
        direction_map = {
            "north": "N",
            "south": "S",
            "east": "E",
            "west": "W",
        }

        for direction, prefix in direction_map.items():
            if self.queues[direction]:
                # Pozrieme sa na prvé auto a jeho konkrétny pruh
                first_car = self.queues[direction][0]
                lane = first_car.get("lane", "S") 
                
                # Zistíme stav presne jeho semaforu (napr. N_L)
                signal_id = f"{prefix}_{lane}"
                
                # OPRAVA: Pustíme ho LEN ak má jeho pruh zelenú!
                if signals.get(signal_id) == "green":
                    vehicle = self.queues[direction].pop(0)
                    vehicle["state"] = "crossing"
                    self.statistics["total_vehicles_passed"] += 1

    def _update_statistics(self) -> None:
        queue_lengths = [len(queue) for queue in self.queues.values()]
        total_waiting = sum(queue_lengths)

        self.statistics["total_vehicles_waiting"] = total_waiting
        self.statistics["max_queue_length"] = max(
            self.statistics["max_queue_length"],
            max(queue_lengths, default=0),
        )

        if queue_lengths:
            self.statistics["average_queue_length"] = round(
                sum(queue_lengths) / len(queue_lengths), 2)

        all_wait_times = []
        for queue in self.queues.values():
            for vehicle in queue:
                all_wait_times.append(vehicle["wait_time"])

        if all_wait_times:
            self.statistics[
                "average_wait_time"] = round(
                    sum(all_wait_times) / len(all_wait_times), 2)
            self.statistics["max_wait_time"] = round(max(all_wait_times), 2)

        if self.statistics["total_vehicles_generated"] > 0:
            util = self.statistics[
                "total_vehicles_passed"] / self.statistics[
                    "total_vehicles_generated"]
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
            self, signals: dict[str, str], cycle_time: float) -> dict:
        vehicles = []
        for queue in self.queues.values():
            vehicles.extend(queue)

        return {
            "type": "state",
            "time": round(self.current_time, 2),
            "cycle_time": cycle_time,
            "signals": signals,
            "vehicles": vehicles,
            "queue_lengths": {
                "north": len(self.queues["north"]),
                "south": len(self.queues["south"]),
                "east": len(self.queues["east"]),
                "west": len(self.queues["west"]),
            },
            "statistics": self.statistics,
        }

    def build_completed_message(self) -> dict:
        return {
            "type": "completed",
            "total_time": round(self.current_time, 2),
            "final_statistics": self.statistics,
        }
