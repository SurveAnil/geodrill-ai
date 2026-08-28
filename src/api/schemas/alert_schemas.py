"""Typed contracts for deterministic predictive-risk alerting."""
from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import List, Optional

from pydantic import AliasChoices, BaseModel, ConfigDict, Field

from src.api.schemas.predictive_schemas import EvidenceCitation
from src.api.schemas.telemetry_schemas import TelemetryPoint


class AlertSeverity(str, Enum):
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class AlertStatus(str, Enum):
    OPEN = "open"
    ACKNOWLEDGED = "acknowledged"


class AlertRecommendation(BaseModel):
    action: str
    rationale: str
    priority: AlertSeverity
    evidence: List[EvidenceCitation] = Field(default_factory=list)


class Alert(BaseModel):
    alert_id: str
    severity: AlertSeverity
    hazard: str
    probability: float = Field(..., ge=0, le=1)
    model_version: str
    rule_basis: List[str] = Field(default_factory=list)
    evidence_basis: List[EvidenceCitation] = Field(default_factory=list)
    recommendations: List[AlertRecommendation] = Field(default_factory=list)
    created_at: datetime
    status: AlertStatus = AlertStatus.OPEN
    acknowledged_at: Optional[datetime] = None
    well_id: str
    measured_depth_m: float


class AlertEvaluationRequest(BaseModel):
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


class AlertEvaluationResponse(BaseModel):
    well_id: str
    measured_depth_m: float
    alerts: List[Alert] = Field(default_factory=list)
    recommendations: List[AlertRecommendation] = Field(default_factory=list)
    evaluated_at: datetime
    evidence_found: bool


class AlertAcknowledgement(BaseModel):
    alert_id: str
    status: AlertStatus
    acknowledged_at: datetime
