from typing import Any, Dict
from pydantic import BaseModel, Field
from app.config import MAX_SIMULATION_DURATION


class TrafficIntensity(BaseModel):
    north: int = Field(..., ge=0, le=100)
    south: int = Field(..., ge=0, le=100)
    east: int = Field(..., ge=0, le=100)
    west: int = Field(..., ge=0, le=100)


class SimulationStartRequest(BaseModel):
    config_id: str
    simulation_duration: int = Field(..., gt=0, le=MAX_SIMULATION_DURATION)
    traffic_intensity: TrafficIntensity


class SimulationStartResponse(BaseModel):
    simulation_id: str
    config_id: str
    websocket_url: str
    status: str


class SimulationResponse(BaseModel):
    simulation_id: str
    config_id: str
    status: str
    simulation_duration: int
    traffic_intensity: TrafficIntensity


class SimulationStatsResponse(BaseModel):
    simulation_id: str
    status: str
    statistics: Dict[str, Any]
