"""
test_db_service.py
==================
Unit tests for database persistence, indexing, and offset-well queries.
"""

import tempfile
import os
from datetime import date
import pytest

from src.api.schemas.document_schemas import ExtractionMethod, ExtractionResult
from src.api.schemas.incident_schemas import Confidence, DrillingEvent, EventType, WellHeader
from src.layer4_knowledge_graph.db_service import DatabaseService


@pytest.fixture
def temp_db():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db = DatabaseService(db_path=path)
    db.init_db()
    yield db
    if os.path.exists(path):
        os.remove(path)


def test_store_and_query_extraction_result(temp_db):
    wh = WellHeader(
        well_id="15/9-F-11B",
        operator="Statoil",
        field_name="Volve",
        spud_date=date(2007, 8, 24),
        latitude=58.4394,
        longitude=1.8875,
        total_depth_m=3200.0,
    )
    event1 = DrillingEvent(
        well_id="15/9-F-11B",
        event_type=EventType.MUD_LOSS,
        depth_m=2450.0,
        formation="Hugin",
        description="Mud loss 15 bbl/hr",
        confidence=Confidence.HIGH,
    )
    event2 = DrillingEvent(
        well_id="15/9-F-11B",
        event_type=EventType.STUCK_PIPE,
        depth_m=2810.0,
        formation="Skagerrak",
        description="Stuck pipe while tripping",
        confidence=Confidence.MEDIUM,
    )
    result = ExtractionResult(
        source_doc="wcr_15_9_f11b.pdf",
        extraction_method=ExtractionMethod.DIGITAL_PARSE,
        well_header=wh,
        events=[event1, event2],
        overall_confidence=Confidence.HIGH,
    )

    temp_db.store_extraction_result(result)

    well = temp_db.get_well("15/9-F-11B")
    assert well is not None
    assert well["operator"] == "Statoil"
    assert well["total_depth_m"] == 3200.0

    events = temp_db.get_well_events("15/9-F-11B")
    assert len(events) == 2
    assert events[0]["event_type"] == "mud_loss"
    assert events[0]["depth_m"] == 2450.0


def test_query_events_near_offset_wells(temp_db):
    # Store Well A
    res_a = ExtractionResult(
        source_doc="well_a.pdf",
        extraction_method=ExtractionMethod.DIGITAL_PARSE,
        well_header=WellHeader(well_id="WELL-A", latitude=58.4, longitude=1.8),
        events=[
            DrillingEvent(
                well_id="WELL-A",
                event_type=EventType.KICK,
                depth_m=2500.0,
                formation="Hugin",
                description="Gas kick 10 bbl gain",
            )
        ],
        overall_confidence=Confidence.HIGH,
    )
    temp_db.store_extraction_result(res_a)

    # Store Well B
    res_b = ExtractionResult(
        source_doc="well_b.pdf",
        extraction_method=ExtractionMethod.DIGITAL_PARSE,
        well_header=WellHeader(well_id="WELL-B", latitude=58.5, longitude=1.9),
        events=[
            DrillingEvent(
                well_id="WELL-B",
                event_type=EventType.MUD_LOSS,
                depth_m=2520.0,
                formation="Hugin",
                description="Total mud loss",
            )
        ],
        overall_confidence=Confidence.HIGH,
    )
    temp_db.store_extraction_result(res_b)

    # Query offset events near 2500m from perspective of new target WELL-C
    matches = temp_db.query_events_near(well_id="WELL-C", depth_m=2500.0, window_m=50.0, formation="Hugin")
    assert len(matches) == 2

    # Query excluding WELL-A
    matches_excluding_a = temp_db.query_events_near(well_id="WELL-A", depth_m=2500.0, window_m=50.0)
    assert len(matches_excluding_a) == 1
    assert matches_excluding_a[0]["well_id"] == "WELL-B"


def test_review_queue_retrieval(temp_db):
    low_conf_result = ExtractionResult(
        source_doc="bad_scan.pdf",
        extraction_method=ExtractionMethod.MANUAL_FLAG,
        well_header=WellHeader(well_id="UNKNOWN"),
        events=[],
        overall_confidence=Confidence.LOW,
        processing_notes="Degraded scan, low text density",
    )
    temp_db.store_extraction_result(low_conf_result)

    review_items = temp_db.get_documents_needing_review()
    assert len(review_items) == 1
    assert review_items[0].source_doc == "bad_scan.pdf"
    assert review_items[0].needs_review is True
