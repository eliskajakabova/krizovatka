from pydantic import BaseModel, field_validator, model_validator
from typing import Optional
from datetime import datetime


class SignalTiming(BaseModel):
    start: int
    duration: int


class ConfigurationRequest(BaseModel):
    name: str
    description: Optional[str] = None
    cycle_duration: int
    signal_timings: dict[str, SignalTiming]

    @field_validator("cycle_duration")
    @classmethod
    def check_cycle(cls, v: int) -> int:
        if not (30 <= v <= 300):
            raise ValueError(f"cycle_duration must be 30–300, got {v}")
        return v

    @model_validator(mode="after")
    def check_timings(self) -> "ConfigurationRequest":
        cd = self.cycle_duration
        for key, t in self.signal_timings.items():
            if not (0 <= t.start < cd):
                raise ValueError(f"'{key}': start must be 0 <= start < {cd}")
            if not (0 <= t.duration <= cd):
                raise ValueError(f"'{key}': duration must be 0 <= duration <= {cd}")
        return self


class ConfigurationResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    cycle_duration: int
    signal_timings: dict
    is_preset: Optional[bool] = False
    cycle_utilization: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# ---------------------------------------------------------------------------
# Simulation models
# ---------------------------------------------------------------------------

class TrafficIntensity(BaseModel):
    north: float
    south: float
    east: float
    west: float

    @field_validator("north", "south", "east", "west")
    @classmethod
    def check_intensity(cls, v: float) -> float:
        if not (0 <= v <= 100):
            raise ValueError(f"traffic_intensity values must be 0–100, got {v}")
        return v


class SimulationRequest(BaseModel):
    config_id: str
    simulation_duration: int
    traffic_intensity: TrafficIntensity
    vehicle_speed: float

    @field_validator("simulation_duration")
    @classmethod
    def check_duration(cls, v: int) -> int:
        if not (1 <= v <= 3600):
            raise ValueError(f"simulation_duration must be 1–3600, got {v}")
        return v

    @field_validator("vehicle_speed")
    @classmethod
    def check_speed(cls, v: float) -> float:
        if not (5 <= v <= 20):
            raise ValueError(f"vehicle_speed must be 5–20, got {v}")
        return v


class SimulationParameters(BaseModel):
    cycle_duration: int
    simulation_duration: int
    traffic_intensity: dict
    vehicle_speed: float


class ExpectedThroughput(BaseModel):
    north: float
    south: float
    east: float
    west: float


class SimulationStartResponse(BaseModel):
    simulation_id: str
    config_id: str
    config_name: str
    websocket_url: str
    status: str
    parameters: SimulationParameters
    expected_throughput: ExpectedThroughput
    started_at: datetime


class CurrentStatistics(BaseModel):
    total_vehicles_passed: Optional[int] = None
    average_wait_time: Optional[float] = None


class FinalStatistics(BaseModel):
    total_vehicles_generated: Optional[int] = None
    total_vehicles_passed: Optional[int] = None
    average_wait_time: Optional[float] = None
    max_wait_time: Optional[float] = None
    intersection_utilization: Optional[float] = None


class SimulationListItem(BaseModel):
    simulation_id: str
    config_id: str
    config_name: Optional[str] = None
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    elapsed_time: Optional[float] = None
    current_statistics: Optional[CurrentStatistics] = None
    final_statistics: Optional[FinalStatistics] = None


class SimulationListResponse(BaseModel):
    simulations: list[SimulationListItem]


class SimulationStopResponse(BaseModel):
    status: str
    simulation_id: str
    elapsed_time: Optional[float] = None
    final_statistics: Optional[FinalStatistics] = None