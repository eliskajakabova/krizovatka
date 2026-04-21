from typing import Dict, List

from pydantic import BaseModel, Field

from app.config import MAX_CYCLE_DURATION, MIN_CYCLE_DURATION


class SignalTiming(BaseModel):
    start: int = Field(..., ge=0)
    duration: int = Field(..., ge=0)


class ConfigurationCreate(BaseModel):
    name: str
    description: str | None = None
    cycle_duration: int = Field(
        ...,
        ge=MIN_CYCLE_DURATION,
        le=MAX_CYCLE_DURATION,
    )
    signal_timings: Dict[str, SignalTiming]


class ConfigurationUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    cycle_duration: int | None = Field(
        None,
        ge=MIN_CYCLE_DURATION,
        le=MAX_CYCLE_DURATION,
    )
    signal_timings: Dict[str, SignalTiming] | None = None


class ConfigurationListItemResponse(BaseModel):
    config_id: str
    name: str
    description: str | None = None
    cycle_duration: int
    is_preset: bool = False
    times_simulated: int = 0
    created_at: str | None = None


class ConfigurationListResponse(BaseModel):
    configurations: list[ConfigurationListItemResponse]


class ConfigurationResponse(BaseModel):
    config_id: str
    name: str
    description: str | None = None
    cycle_duration: int
    signal_timings: Dict[str, SignalTiming]
    is_preset: bool = False
    cycle_utilization: float | None = None
    created_at: str | None = None
    updated_at: str | None = None
    times_simulated: int = 0


class ConflictDetail(BaseModel):
    signal_a: str
    signal_b: str
    error: str


class ConfigurationValidationRequest(BaseModel):
    cycle_duration: int = Field(
        ...,
        ge=MIN_CYCLE_DURATION,
        le=MAX_CYCLE_DURATION,
    )
    signal_timings: Dict[str, SignalTiming]


class ConfigurationValidationResponse(BaseModel):
    valid: bool
    conflicts_detected: List[ConflictDetail] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    cycle_utilization: float
