"""Deterministic, explainable hazard-probability baseline.

This is intentionally not a trained model: the repository contains incident
records but no outcome labels.  Historical events are evidence, not labels.
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Sequence

from src.api.schemas.predictive_schemas import (
    EvidenceCitation,
    FeatureContribution,
    HazardPrediction,
)
from src.api.schemas.telemetry_schemas import TelemetryPoint
from src.layer5_copilot.incident_correlator import correlate_at_depth

MODEL_VERSION = "heuristic-baseline-v1"
HAZARDS = ("mud_loss", "stuck_pipe", "kick", "overpressure", "torque_spike", "cementing_issue")

# Signals are deliberately modest; this service must not imply calibrated odds.
EVENT_TO_HAZARD = {hazard: hazard for hazard in HAZARDS}
BASE_PRIOR = 0.02


def _level(probability: float) -> str:
    if probability >= 0.60:
        return "high"
    if probability >= 0.25:
        return "medium"
    return "low"


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, round(value, 6)))


def extract_features(current: TelemetryPoint, recent: Sequence[TelemetryPoint]) -> Dict[str, float]:
    """Return bounded, named features so every prediction is auditable."""
    samples = list(recent)
    features: Dict[str, float] = {
        "standpipe_pressure_normalized": current.standpipe_pressure / 20_000.0,
        "flow_rate_normalized": current.flow_rate / 5_000.0,
        "torque_normalized": current.torque / 500.0,
        "mud_weight_normalized": current.mud_weight_sg / 3.0,
        "wob_normalized": current.wob / 200.0,
        "rop_normalized": current.rop / 500.0,
    }
    if samples:
        avg_torque = sum(p.torque for p in samples) / len(samples)
        avg_pressure = sum(p.standpipe_pressure for p in samples) / len(samples)
        avg_flow = sum(p.flow_rate for p in samples) / len(samples)
        features["torque_change_normalized"] = max(0.0, current.torque - avg_torque) / 500.0
        features["pressure_change_normalized"] = max(0.0, current.standpipe_pressure - avg_pressure) / 20_000.0
        features["flow_drop_normalized"] = max(0.0, avg_flow - current.flow_rate) / 5_000.0
    else:
        features.update({"torque_change_normalized": 0.0, "pressure_change_normalized": 0.0, "flow_drop_normalized": 0.0})
    return {key: _clamp(value) for key, value in features.items()}


def _citation(event: Mapping[str, Any]) -> EvidenceCitation:
    return EvidenceCitation(
        event_id=event.get("event_id"), well_id=event.get("well_id"),
        event_type=event.get("event_type"), depth_m=event.get("depth_m"),
        source_doc=event.get("source_doc"), source_page=event.get("source_page"),
        source_snippet=event.get("source_snippet"),
    )


def predict_hazards(
    current: TelemetryPoint,
    recent: Sequence[TelemetryPoint] = (),
    *,
    formation: str | None = None,
    window_m: float = 100.0,
    events: Iterable[Mapping[str, Any]] | None = None,
) -> Dict[str, HazardPrediction]:
    features = extract_features(current, recent)
    correlated = list(events) if events is not None else correlate_at_depth(
        current.well_id, current.measured_depth_m, formation=formation, window_m=window_m
    )
    output: Dict[str, HazardPrediction] = {}
    for hazard in HAZARDS:
        relevant = [event for event in correlated if event.get("event_type") == hazard]
        # Repeated independent offsets increase evidence, with diminishing returns.
        historical_signal = min(0.45, 0.12 * len(relevant))
        weights = {
            "mud_loss": {"flow_drop_normalized": 0.20, "mud_weight_normalized": 0.04},
            "stuck_pipe": {"wob_normalized": 0.12, "torque_change_normalized": 0.20, "rop_normalized": 0.06},
            "kick": {"flow_drop_normalized": 0.14, "pressure_change_normalized": 0.16, "mud_weight_normalized": 0.08},
            "overpressure": {"pressure_change_normalized": 0.28, "standpipe_pressure_normalized": 0.08},
            "torque_spike": {"torque_change_normalized": 0.35, "torque_normalized": 0.08},
            "cementing_issue": {"mud_weight_normalized": 0.03, "pressure_change_normalized": 0.04},
        }[hazard]
        contributions = [
            FeatureContribution(
                name=name, value=features[name], contribution=round(features[name] * weight, 6),
                explanation=f"{name.replace('_', ' ')} contributes {weight:.2f} at this baseline",
            )
            for name, weight in weights.items()
        ]
        contributions.sort(key=lambda item: (-item.contribution, item.name))
        probability = _clamp(BASE_PRIOR + historical_signal + sum(item.contribution for item in contributions))
        output[hazard] = HazardPrediction(
            probability=probability, risk_level=_level(probability),
            top_contributing_features=contributions[:3],
            evidence=[_citation(event) for event in relevant],
            citations=[_citation(event) for event in relevant],
        )
    return output
