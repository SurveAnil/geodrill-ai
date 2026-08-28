from datetime import datetime, timedelta, timezone

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.layer1_ingestion.telemetry_store import telemetry_store


def point(index: int = 0, **overrides):
    value = {
        "timestamp": (datetime.now(timezone.utc) + timedelta(milliseconds=index)).isoformat(),
        "well_id": "W-1",
        "measuredDepthM": 1000 + index,
        "trueVerticalDepthM": 950 + index,
        "rop": 20,
        "wob": 10,
        "torque": 8,
        "flowRate": 700,
        "standpipePressure": 3000,
        "mudWeightSg": 1.35,
    }
    value.update(overrides)
    return value


@pytest.fixture
def client():
    telemetry_store.clear()
    with TestClient(app) as test_client:
        yield test_client
    telemetry_store.clear()


def test_ingests_valid_telemetry(client):
    response = client.post("/api/v1/telemetry", json={"points": [point()]})
    assert response.status_code == 202
    assert response.json() == {"accepted": 1}


def test_rejects_non_finite_or_out_of_range_values(client):
    assert client.post("/api/v1/telemetry", json={"points": [point(rop=501)]}).status_code == 422
    assert client.post("/api/v1/telemetry", json={"points": [point(rop="NaN")]}).status_code == 422


def test_rejects_batches_over_limit(client):
    response = client.post("/api/v1/telemetry", json={"points": [point(i) for i in range(101)]})
    assert response.status_code == 422


def test_returns_recent_points_in_order_and_honors_limit(client):
    assert client.post("/api/v1/telemetry", json={"points": [point(i) for i in range(3)]}).status_code == 202
    response = client.get("/api/v1/telemetry/recent", params={"well_id": "W-1", "limit": 2})
    assert response.status_code == 200
    data = response.json()
    assert data["well_id"] == "W-1"
    assert [item["measured_depth_m"] for item in data["points"]] == [1001, 1002]
