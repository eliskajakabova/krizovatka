from typing import Any, Dict

from pydantic import BaseModel, Field

from app.config import MAX_SIMULATION_DURATION


class TrafficIntensity(BaseModel):
    north: int = Field(..., ge=0, le=100)
    south: int = Field(..., ge=0, le=100)
    east: int = Field(..., ge=0, le=100)
    west: int = Field(..., ge=0, le=100)


class SimulationParameters(BaseModel):
    cycle_duration: int
    simulation_duration: int
    traffic_intensity: TrafficIntensity


class SimulationStartRequest(BaseModel):
    config_id: str
    simulation_duration: int = Field(..., gt=0, le=MAX_SIMULATION_DURATION)
    traffic_intensity: TrafficIntensity


class SimulationStartResponse(BaseModel):
    simulation_id: str
    config_id: str
    config_name: str | None = None
    websocket_url: str
    status: str
    parameters: SimulationParameters
    started_at: str


class SimulationResponse(BaseModel):
    simulation_id: str
    config_id: str
    status: str
    simulation_duration: int
    traffic_intensity: TrafficIntensity
    started_at: str
    completed_at: str | None = None
    elapsed_time: float | None = None


class SimulationStatsResponse(BaseModel):
    simulation_id: str
    status: str
    statistics: Dict[str, Any]
