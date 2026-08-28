"""Contract and determinism tests for the Phase 3 predictive baseline."""
from datetime import datetime, timezone

from fastapi.testclient import TestClient

from src.api.main import app
from src.api.schemas.telemetry_schemas import TelemetryPoint
from src.layer5_copilot.hazard_prediction import HAZARDS, predict_hazards


def _point(**overrides) -> TelemetryPoint:
    values = {
        "timestamp": datetime(2026, 1, 1, tzinfo=timezone.utc),
        "well_id": "baseline-well",
        "measured_depth_m": 2500,
        "true_vertical_depth_m": 2400,
        "rop": 20,
        "wob": 10,
        "torque": 8,
        "flow_rate": 700,
        "standpipe_pressure": 3000,
        "mud_weight_sg": 1.35,
    }
    values.update(overrides)
    return TelemetryPoint(**values)


def test_predictions_cover_all_hazards_and_are_bounded():
    result = predict_hazards(_point(), events=[])
    assert set(result) == set(HAZARDS)
    assert all(0 <= item.probability <= 1 for item in result.values())
    assert all(item.risk_level in {"low", "medium", "high"} for item in result.values())


def test_predictions_are_deterministic_and_cite_offset_evidence():
    event = {
        "event_id": 7, "well_id": "offset-1", "event_type": "kick",
        "depth_m": 2490, "source_doc": "offset.pdf", "source_page": 4,
        "source_snippet": "kick observed",
    }
    first = predict_hazards(_point(), events=[event])
    second = predict_hazards(_point(), events=[event])
    assert first == second
    assert first["kick"].evidence[0].source_doc == "offset.pdf"


def test_predictive_risk_api_validates_and_returns_metadata():
    point = _point().model_dump(mode="json")
    with TestClient(app) as client:
        response = client.post("/api/v1/predictive-risk", json={"current_telemetry": point})
        assert response.status_code == 200
        body = response.json()
        assert body["model_version"] == "heuristic-baseline-v1"
        assert set(body["hazards"]) == set(HAZARDS)
        assert body["metadata"]["trained"] is False
        invalid = client.post("/api/v1/predictive-risk", json={"current_telemetry": {"well_id": "x"}})
        assert invalid.status_code == 422
