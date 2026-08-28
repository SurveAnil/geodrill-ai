"""Typed contracts for trajectory and correlation analytics."""
from __future__ import annotations
import math
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

class SurveyStation(BaseModel):
    md: float = Field(..., ge=0)
    inclination: float = Field(0.0, ge=0, le=180)
    azimuth: float = Field(0.0, ge=0, lt=360)
    @field_validator("md", "inclination", "azimuth")
    @classmethod
    def finite(cls, value: float) -> float:
        if not math.isfinite(value): raise ValueError("value must be finite")
        return value

class TrajectoryRequest(BaseModel):
    stations: List[SurveyStation] = Field(..., min_length=1, max_length=10000)

class TrajectoryStation(SurveyStation):
    northing: float
    easting: float
    tvd: float

class FormationCorrelationRequest(BaseModel):
    stations: List[SurveyStation] = Field(..., min_length=1, max_length=10000)
    formation_tops: List[dict] = Field(default_factory=list, max_length=1000)