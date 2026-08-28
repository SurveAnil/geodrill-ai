"""Validation contracts for real-time drilling telemetry."""
from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import List

from pydantic import AliasChoices, BaseModel, ConfigDict, Field, field_validator


class TelemetryPoint(BaseModel):
    """One sensor sample. Values are deliberately bounded before storage."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    timestamp: datetime
    well_id: str = Field(..., min_length=1, max_length=200)
    measured_depth_m: float = Field(..., ge=0, le=100_000, validation_alias=AliasChoices("measured_depth_m", "measuredDepthM"))
    true_vertical_depth_m: float = Field(..., ge=0, le=100_000, validation_alias=AliasChoices("true_vertical_depth_m", "trueVerticalDepthM"))
    rop: float = Field(..., ge=0, le=500, description="Rate of penetration (m/hr)")
    wob: float = Field(..., ge=0, le=200, description="Weight on bit (klbs)")
    torque: float = Field(..., ge=0, le=500, description="Torque (kft-lb)")
    flow_rate: float = Field(..., ge=0, le=5_000, validation_alias=AliasChoices("flow_rate", "flowRate"))
    standpipe_pressure: float = Field(..., ge=0, le=20_000, validation_alias=AliasChoices("standpipe_pressure", "standpipePressure"))
    mud_weight_sg: float = Field(..., gt=0, le=3.0, validation_alias=AliasChoices("mud_weight_sg", "mudWeightSg"))

    @field_validator("timestamp")
    @classmethod
    def timestamp_utc(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)

    @field_validator(
        "measured_depth_m", "true_vertical_depth_m", "rop", "wob", "torque",
        "flow_rate", "standpipe_pressure", "mud_weight_sg",
    )
    @classmethod
    def finite(cls, value: float) -> float:
        if not math.isfinite(value):
            raise ValueError("telemetry values must be finite")
        return value


class TelemetryBatch(BaseModel):
    """At most ten seconds of 10 Hz samples per request."""

    model_config = ConfigDict(extra="forbid")
    points: List[TelemetryPoint] = Field(..., min_length=1, max_length=100)


class TelemetryRecentResponse(BaseModel):
    well_id: str
    points: List[TelemetryPoint]
