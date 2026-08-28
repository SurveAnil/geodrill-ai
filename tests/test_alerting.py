from datetime import datetime, timezone

from src.api.schemas.telemetry_schemas import TelemetryPoint
from src.layer5_copilot.alerting import alert_store, evaluate_alerts


def _point(**changes):
    values = dict(
        timestamp=datetime.now(timezone.utc), well_id="alert-well",
        measured_depth_m=2500, true_vertical_depth_m=2400, rop=20,
        wob=10, torque=450, flow_rate=700, standpipe_pressure=3000,
        mud_weight_sg=1.35,
    )
    values.update(changes)
    return TelemetryPoint(**values)


def setup_function():
    alert_store.clear()


def test_threshold_requires_evidence_and_returns_action():
    alerts, recommendations, evidence = evaluate_alerts(
        _point(), events=[{"event_id": 1, "well_id": "offset", "event_type": "torque_spike", "depth_m": 2500}]
    )
    assert evidence is True
    assert alerts[0].hazard == "torque_spike"
    assert alerts[0].rule_basis
    assert recommendations[0].evidence[0].event_id == 1


def test_duplicate_evaluation_is_suppressed_during_cooldown():
    event = [{"event_id": 1, "well_id": "offset", "event_type": "torque_spike", "depth_m": 2500}]
    assert len(evaluate_alerts(_point(), events=event)[0]) == 1
    assert evaluate_alerts(_point(), events=event)[0] == []


def test_acknowledgement_changes_state():
    alerts, _, _ = evaluate_alerts(
        _point(), events=[{"event_id": 1, "well_id": "offset", "event_type": "torque_spike", "depth_m": 2500}]
    )
    acknowledged = alert_store.acknowledge(alerts[0].alert_id)
    assert acknowledged.status.value == "acknowledged"
    assert acknowledged.acknowledged_at is not None


def test_no_evidence_does_not_emit_alert():
    alerts, _, evidence = evaluate_alerts(_point(), events=[])
    assert alerts == []
    assert evidence is False
