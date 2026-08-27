"""
test_risk_scoring.py
====================
Comprehensive tests for Stage 3: Incident Correlation & Risk Scoring Layer.

Tests cover:
  1. correlate_ahead() picks up known events in the lookahead interval
  2. correlate_ahead() returns empty when no events match
  3. score_risk([]) returns low/0
  4. score_risk() with high-severity event returns at least medium
  5. score_risk() is deterministic
  6. GET /api/v1/incidents/risk-check end-to-end
  7. Invalid well_id returns 404
  8. direction="ahead" asymmetric window in query_events_near
"""

import os
import tempfile
from datetime import date

import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.api.schemas.document_schemas import ExtractionMethod, ExtractionResult
from src.api.schemas.incident_schemas import Confidence, DrillingEvent, EventType, WellHeader
from src.layer4_knowledge_graph.db_service import DatabaseService, db_service
from src.layer5_copilot.incident_correlator import correlate_ahead, correlate_at_depth
from src.layer5_copilot.risk_scorer import score_risk, EVENT_SEVERITY_WEIGHTS


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def populated_db():
    """Creates a temporary DB with two known wells and their events."""
    fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    test_db = DatabaseService(db_path=db_path)
    test_db.init_db()

    # Well 1: 15/9-F-11B — mud_loss at 2450m, stuck_pipe at 2810m
    res_a = ExtractionResult(
        source_doc="wcr_volve_15_9_f11b.pdf",
        extraction_method=ExtractionMethod.DIGITAL_PARSE,
        well_header=WellHeader(
            well_id="15/9-F-11B",
            operator="Statoil ASA",
            field_name="Volve",
            spud_date=date(2007, 8, 24),
            latitude=58.4394,
            longitude=1.8875,
            total_depth_m=3200.0,
        ),
        events=[
            DrillingEvent(
                well_id="15/9-F-11B",
                event_type=EventType.MUD_LOSS,
                depth_m=2450.0,
                formation="Hugin Formation",
                event_date=date(2007, 9, 12),
                description="Partial mud losses of 15 bbl/hr.",
                symptom="Pit level dropped steadily over 2 hours",
                action_taken="Pumped LCM pill (50 bbl)",
                confidence=Confidence.HIGH,
                source_page=3,
                source_snippet="at 2450m encountered mud loss of 15 bbl/hr, pumped LCM pill",
            ),
            DrillingEvent(
                well_id="15/9-F-11B",
                event_type=EventType.STUCK_PIPE,
                depth_m=2810.0,
                formation="Skagerrak Formation",
                event_date=date(2007, 9, 18),
                description="Mechanical stuck pipe while tripping in tight hole.",
                action_taken="Worked pipe free with jarring",
                confidence=Confidence.MEDIUM,
                source_page=5,
                source_snippet="stuck pipe at 2810m, freed with jarring",
            ),
        ],
        overall_confidence=Confidence.HIGH,
    )

    # Well 2: 15/9-F-12 — kick at 2510m
    res_b = ExtractionResult(
        source_doc="ddr_volve_15_9_f12.pdf",
        extraction_method=ExtractionMethod.DIGITAL_PARSE,
        well_header=WellHeader(
            well_id="15/9-F-12",
            operator="Statoil ASA",
            field_name="Volve",
            latitude=58.4410,
            longitude=1.8890,
            total_depth_m=3100.0,
        ),
        events=[
            DrillingEvent(
                well_id="15/9-F-12",
                event_type=EventType.KICK,
                depth_m=2510.0,
                formation="Hugin Formation",
                event_date=date(2008, 3, 5),
                description="Gas kick detected with 10 bbl pit gain.",
                action_taken="Shut in well, circulated kick out",
                confidence=Confidence.HIGH,
                source_page=2,
                source_snippet="gas kick detected, 10 bbl pit gain",
            ),
        ],
        overall_confidence=Confidence.HIGH,
    )

    test_db.store_extraction_result(res_a)
    test_db.store_extraction_result(res_b)

    # Also register the hypothetical active well (15/9-F-13)
    # so that the risk-check endpoint can validate its existence
    res_c = ExtractionResult(
        source_doc="placeholder_f13.pdf",
        extraction_method=ExtractionMethod.DIGITAL_PARSE,
        well_header=WellHeader(
            well_id="15/9-F-13",
            operator="Statoil ASA",
            field_name="Volve",
            latitude=58.4420,
            longitude=1.8900,
        ),
        events=[],
        overall_confidence=Confidence.HIGH,
    )
    test_db.store_extraction_result(res_c)

    yield test_db

    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture
def test_client(populated_db):
    """Test client with the populated_db swapped in as the singleton."""
    original_path = db_service.db_path
    db_service.db_path = populated_db.db_path

    with TestClient(app) as client:
        yield client

    db_service.db_path = original_path


# ---------------------------------------------------------------------------
# Unit tests: query_events_near direction parameter
# ---------------------------------------------------------------------------

def test_query_events_near_direction_ahead(populated_db):
    """direction='ahead' only returns events AHEAD of the current depth."""
    # From perspective of a new well at 2440m, looking ahead 80m → [2440, 2520]
    events = populated_db.query_events_near(
        well_id="15/9-F-13",
        depth_m=2440.0,
        window_m=80.0,
        direction="ahead",
    )
    depths = [e["depth_m"] for e in events]
    # mud_loss at 2450m and kick at 2510m should be found
    assert 2450.0 in depths
    assert 2510.0 in depths
    # stuck_pipe at 2810m should NOT be in range
    assert 2810.0 not in depths


def test_query_events_near_direction_both_is_symmetric(populated_db):
    """direction='both' (default) searches symmetrically."""
    events = populated_db.query_events_near(
        well_id="15/9-F-13",
        depth_m=2480.0,
        window_m=50.0,
        direction="both",
    )
    depths = [e["depth_m"] for e in events]
    # Both 2450 (behind) and 2510 (ahead) should be found
    assert 2450.0 in depths
    assert 2510.0 in depths


# ---------------------------------------------------------------------------
# Unit tests: correlate_ahead
# ---------------------------------------------------------------------------

def test_correlate_ahead_picks_up_known_events(populated_db):
    """
    A hypothetical third well (15/9-F-13) approaching 2440m in Hugin Formation
    with 80m lookahead should pick up mud_loss at 2450m and kick at 2510m.
    """
    events = correlate_ahead(
        active_well_id="15/9-F-13",
        current_depth_m=2440.0,
        formation="Hugin Formation",
        lookahead_m=80.0,
        db=populated_db,
    )
    assert len(events) == 2
    event_types = {e["event_type"] for e in events}
    assert "mud_loss" in event_types
    assert "kick" in event_types

    # Citation fields must be present
    for ev in events:
        assert ev["well_id"] in ("15/9-F-11B", "15/9-F-12")
        assert ev["source_doc"] is not None
        assert ev["source_page"] is not None


def test_correlate_ahead_empty_result(populated_db):
    """Depth/formation with no historical events returns empty list."""
    events = correlate_ahead(
        active_well_id="15/9-F-13",
        current_depth_m=1000.0,
        formation="Nonexistent Formation",
        lookahead_m=50.0,
        db=populated_db,
    )
    assert events == []


def test_correlate_ahead_excludes_active_well(populated_db):
    """correlate_ahead should exclude the active well from results."""
    # From 15/9-F-11B's own perspective, its own events should not appear
    events = correlate_ahead(
        active_well_id="15/9-F-11B",
        current_depth_m=2440.0,
        lookahead_m=80.0,
        db=populated_db,
    )
    well_ids = {e["well_id"] for e in events}
    assert "15/9-F-11B" not in well_ids


def test_correlate_at_depth_symmetric(populated_db):
    """correlate_at_depth searches both directions."""
    events = correlate_at_depth(
        active_well_id="15/9-F-13",
        current_depth_m=2480.0,
        window_m=50.0,
        db=populated_db,
    )
    depths = {e["depth_m"] for e in events}
    assert 2450.0 in depths  # behind
    assert 2510.0 in depths  # ahead


# ---------------------------------------------------------------------------
# Unit tests: score_risk
# ---------------------------------------------------------------------------

def test_score_risk_empty_returns_low():
    """score_risk([]) returns low/0, not an error."""
    result = score_risk([])
    assert result["risk_level"] == "low"
    assert result["risk_score"] == 0
    assert len(result["contributing_events"]) == 0
    assert "No historical incidents" in result["explanation"]


def test_score_risk_stuck_pipe_returns_at_least_medium():
    """stuck_pipe has severity weight 9 — a single event should push to at least medium."""
    events = [
        {
            "event_id": 2,
            "well_id": "15/9-F-11B",
            "event_type": "stuck_pipe",
            "depth_m": 2810.0,
            "formation": "Skagerrak Formation",
            "description": "Stuck pipe while tripping",
            "confidence": "medium",
            "source_doc": "wcr_volve_15_9_f11b.pdf",
            "source_page": 5,
            "source_snippet": "stuck pipe at 2810m",
        }
    ]
    result = score_risk(events)
    # 1 event * 8 (freq) + 9 * 3 (severity) = 35 → medium
    assert result["risk_level"] in ("medium", "high")
    assert result["risk_score"] >= 30
    assert len(result["contributing_events"]) == 1
    assert result["contributing_events"][0]["source_doc"] == "wcr_volve_15_9_f11b.pdf"
    assert result["contributing_events"][0]["source_page"] == 5


def test_score_risk_multiple_severe_events_returns_high():
    """Multiple high-severity events should push score to high."""
    events = [
        {"event_id": 1, "well_id": "W-A", "event_type": "kick", "depth_m": 2500,
         "formation": "F", "description": "kick", "source_doc": "a.pdf", "source_page": 1},
        {"event_id": 2, "well_id": "W-B", "event_type": "stuck_pipe", "depth_m": 2510,
         "formation": "F", "description": "stuck", "source_doc": "b.pdf", "source_page": 2},
        {"event_id": 3, "well_id": "W-C", "event_type": "overpressure", "depth_m": 2520,
         "formation": "F", "description": "overp", "source_doc": "c.pdf", "source_page": 3},
    ]
    result = score_risk(events)
    # 3 * 8 + (10+9+8)*3 = 24 + 81 = 105 → capped at 100 → high
    assert result["risk_level"] == "high"
    assert result["risk_score"] == 100.0


def test_score_risk_is_deterministic():
    """Same input always produces the same output — no randomness."""
    events = [
        {"event_id": 1, "well_id": "W-A", "event_type": "mud_loss", "depth_m": 2450,
         "description": "loss", "source_doc": "a.pdf", "source_page": 1},
    ]
    result1 = score_risk(events)
    result2 = score_risk(events)
    assert result1["risk_score"] == result2["risk_score"]
    assert result1["risk_level"] == result2["risk_level"]
    assert result1["explanation"] == result2["explanation"]


def test_score_risk_citation_fields_preserved():
    """Every contributing event must carry full citation fields."""
    events = [
        {
            "event_id": 99,
            "well_id": "TEST-WELL",
            "event_type": "kick",
            "depth_m": 3000.0,
            "formation": "Test Fm",
            "event_date": "2020-01-01",
            "description": "Test kick",
            "confidence": "high",
            "source_doc": "test_report.pdf",
            "source_page": 7,
            "source_snippet": "kick at 3000m",
        }
    ]
    result = score_risk(events)
    ce = result["contributing_events"][0]
    assert ce["well_id"] == "TEST-WELL"
    assert ce["source_doc"] == "test_report.pdf"
    assert ce["source_page"] == 7
    assert ce["source_snippet"] == "kick at 3000m"


# ---------------------------------------------------------------------------
# Integration tests: GET /api/v1/incidents/risk-check
# ---------------------------------------------------------------------------

def test_risk_check_endpoint_elevated_risk(test_client):
    """
    Approaching 2440m in Hugin Formation with 80m lookahead should yield
    elevated risk from the known mud_loss at 2450m and kick at 2510m.
    """
    response = test_client.get(
        "/api/v1/incidents/risk-check",
        params={
            "well_id": "15/9-F-13",
            "current_depth_m": 2440.0,
            "formation": "Hugin Formation",
            "lookahead_m": 80.0,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["well_id"] == "15/9-F-13"
    assert data["current_depth_m"] == 2440.0
    assert data["lookahead_m"] == 80.0
    assert data["risk_level"] in ("medium", "high")
    assert data["risk_score"] > 0
    assert len(data["contributing_events"]) == 2
    assert "rule-based" in data["explanation"]

    # Verify citation fields on contributing events
    for ev in data["contributing_events"]:
        assert ev["well_id"] in ("15/9-F-11B", "15/9-F-12")
        assert ev["source_doc"] is not None
        assert ev["source_page"] is not None


def test_risk_check_endpoint_low_risk(test_client):
    """Querying at a depth with no historical incidents returns low risk."""
    response = test_client.get(
        "/api/v1/incidents/risk-check",
        params={
            "well_id": "15/9-F-13",
            "current_depth_m": 1000.0,
            "lookahead_m": 50.0,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert data["risk_level"] == "low"
    assert data["risk_score"] == 0
    assert len(data["contributing_events"]) == 0


def test_risk_check_endpoint_unknown_well_returns_404(test_client):
    """Invalid/unknown well_id should return 404, not 500."""
    response = test_client.get(
        "/api/v1/incidents/risk-check",
        params={
            "well_id": "NONEXISTENT-WELL",
            "current_depth_m": 2500.0,
        },
    )
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_risk_check_endpoint_missing_depth_returns_422(test_client):
    """Missing current_depth_m should return 422 (FastAPI validation)."""
    response = test_client.get(
        "/api/v1/incidents/risk-check",
        params={"well_id": "15/9-F-13"},
    )
    assert response.status_code == 422
