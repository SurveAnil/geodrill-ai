"""Deterministic, thread-safe alert evaluation and bounded alert state."""
from __future__ import annotations

from collections import OrderedDict
from datetime import datetime, timedelta, timezone
from hashlib import sha256
from threading import Lock
from typing import Iterable, Mapping, Optional, Sequence

from src.api.schemas.alert_schemas import (
    Alert,
    AlertAcknowledgement,
    AlertRecommendation,
    AlertSeverity,
    AlertStatus,
)
from src.api.schemas.predictive_schemas import EvidenceCitation
from src.api.schemas.telemetry_schemas import TelemetryPoint
from src.layer5_copilot.hazard_prediction import MODEL_VERSION, predict_hazards


class AlertStore:
    """Bounded process-local state; acknowledgement and cooldown are atomic."""

    def __init__(self, max_alerts: int = 1000, cooldown_seconds: int = 300) -> None:
        self._alerts: OrderedDict[str, Alert] = OrderedDict()
        self._cooldown = timedelta(seconds=cooldown_seconds)
        self._max_alerts = max_alerts
        self._lock = Lock()

    def get_or_create(self, alert: Alert) -> tuple[Alert, bool]:
        with self._lock:
            existing = self._alerts.get(alert.alert_id)
            now = alert.created_at
            if existing is not None and now - existing.created_at < self._cooldown:
                return existing, False
            self._alerts[alert.alert_id] = alert
            self._alerts.move_to_end(alert.alert_id)
            while len(self._alerts) > self._max_alerts:
                self._alerts.popitem(last=False)
            return alert, True

    def acknowledge(self, alert_id: str) -> Optional[Alert]:
        with self._lock:
            alert = self._alerts.get(alert_id)
            if alert is None:
                return None
            acknowledged = alert.model_copy(
                update={"status": AlertStatus.ACKNOWLEDGED, "acknowledged_at": datetime.now(timezone.utc)}
            )
            self._alerts[alert_id] = acknowledged
            return acknowledged

    def clear(self) -> None:
        with self._lock:
            self._alerts.clear()


alert_store = AlertStore()


def _citation(event: Mapping[str, object]) -> EvidenceCitation:
    return EvidenceCitation(
        event_id=event.get("event_id"), well_id=event.get("well_id"),
        event_type=event.get("event_type"), depth_m=event.get("depth_m"),
        source_doc=event.get("source_doc"), source_page=event.get("source_page"),
        source_snippet=event.get("source_snippet"),
    )


def _recommendation(hazard: str, evidence: Sequence[EvidenceCitation],
                    severity: AlertSeverity) -> AlertRecommendation:
    actions = {
        "kick": "Pause drilling and verify flow, pit volume, and well-control barriers.",
        "mud_loss": "Reduce pumps and check losses; confirm active pit volume and returns.",
        "stuck_pipe": "Stop rotation escalation and review torque/WOB; prepare a freeing plan.",
        "overpressure": "Hold parameters and verify pressure limits with the drilling supervisor.",
        "torque_spike": "Reduce WOB/rotation and inspect torque trend before proceeding.",
        "cementing_issue": "Stop progression and verify cement placement and pressure test results.",
    }
    action = actions.get(hazard, "Hold current parameters and perform a documented safety check.")
    return AlertRecommendation(
        action=action,
        rationale=f"Deterministic safety rules indicate {severity.value} concern for {hazard}.",
        priority=severity,
        evidence=list(evidence),
    )


def evaluate_alerts(
    current: TelemetryPoint,
    recent: Sequence[TelemetryPoint] = (),
    *,
    formation: Optional[str] = None,
    window_m: float = 100.0,
    events: Optional[Iterable[Mapping[str, object]]] = None,
) -> tuple[list[Alert], list[AlertRecommendation], bool]:
    """Evaluate only deterministic rules; no LLM output participates."""
    supplied_events = list(events) if events is not None else None
    predictions = predict_hazards(
        current, recent, formation=formation, window_m=window_m, events=supplied_events
    )
    evidence_found = any(prediction.evidence for prediction in predictions.values())
    now = datetime.now(timezone.utc)
    alerts: list[Alert] = []
    recommendations: list[AlertRecommendation] = []
    for hazard, prediction in predictions.items():
        evidence = prediction.evidence
        citations = list(evidence)
        # Historical evidence is required for predictive alerts. A no-evidence
        # evaluation remains observable through a conservative recommendation.
        if not evidence:
            if prediction.probability >= 0.60:
                recommendations.append(AlertRecommendation(
                    action="Verify sensors and obtain offset-well evidence before escalating.",
                    rationale="High heuristic score has no corroborating historical incident.",
                    priority=AlertSeverity.MEDIUM, evidence=[],
                ))
            continue
        hard_rule = (
            (hazard == "torque_spike" and current.torque >= 400)
            or (hazard == "overpressure" and current.standpipe_pressure >= 16_000)
            or (hazard == "mud_loss" and current.flow_rate <= 500)
        )
        if prediction.probability < 0.25 and not hard_rule:
            continue
        severity = AlertSeverity.CRITICAL if prediction.probability >= 0.60 else AlertSeverity.MEDIUM
        rule_basis = [
            (
                f"probability >= {0.60 if severity == AlertSeverity.CRITICAL else 0.25:.2f}"
                if prediction.probability >= 0.25 else "deterministic sensor safety threshold crossed"
            ),
            "historical offset evidence present within configured depth window",
        ]
        recommendation = _recommendation(hazard, citations, severity)
        key = f"{current.well_id}|{hazard}|{severity.value}"
        alert_id = sha256(key.encode("utf-8")).hexdigest()[:24]
        candidate = Alert(
            alert_id=alert_id, severity=severity, hazard=hazard,
            probability=prediction.probability, model_version=MODEL_VERSION,
            rule_basis=rule_basis, evidence_basis=citations,
            recommendations=[recommendation], created_at=now,
            well_id=current.well_id, measured_depth_m=current.measured_depth_m,
        )
        stored, created = alert_store.get_or_create(candidate)
        if created:
            alerts.append(stored)
        recommendations.append(recommendation)
    return alerts, recommendations, evidence_found
