"""Typed contracts for the Phase 3 predictive-risk baseline."""
from __future__ import annotations

from typing import Dict, List, Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from src.api.schemas.telemetry_schemas import TelemetryPoint


class PredictiveRiskRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    current_telemetry: TelemetryPoint = Field(
        ..., validation_alias=AliasChoices("current_telemetry", "telemetry", "currentTelemetry")
    )
    recent_telemetry: List[TelemetryPoint] = Field(
        default_factory=list, max_length=100,
        validation_alias=AliasChoices("recent_telemetry", "telemetry_history", "recentTelemetry"),
    )
    formation: Optional[str] = Field(None, max_length=200)
    window_m: float = Field(100.0, gt=0, le=10_000)


class FeatureContribution(BaseModel):
    name: str
    value: float
    contribution: float
    explanation: str


class EvidenceCitation(BaseModel):
    event_id: Optional[int] = None
    well_id: Optional[str] = None
    event_type: Optional[str] = None
    depth_m: Optional[float] = None
    source_doc: Optional[str] = None
    source_page: Optional[int] = None
    source_snippet: Optional[str] = None


class HazardPrediction(BaseModel):
    probability: float = Field(..., ge=0, le=1)
    risk_level: str
    top_contributing_features: List[FeatureContribution]
    evidence: List[EvidenceCitation]
    citations: List[EvidenceCitation]


class PredictiveRiskResponse(BaseModel):
    model_version: str
    well_id: str
    measured_depth_m: float
    hazards: Dict[str, HazardPrediction]
    metadata: Dict[str, object]
