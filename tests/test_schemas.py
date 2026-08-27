"""
test_schemas.py
===============
Unit tests for domain Pydantic schemas and contract validation.
"""

from datetime import date
import pytest
from pydantic import ValidationError

from src.api.schemas.incident_schemas import (
    WellHeader,
    DrillingEvent,
    EventType,
    Confidence,
)
from src.api.schemas.document_schemas import (
    ExtractionMethod,
    ExtractionResult,
    PageContent,
    IngestResult,
)


def test_well_header_valid():
    wh = WellHeader(
        well_id="15/9-F-11B",
        operator="Statoil ASA",
        field_name="Volve",
        spud_date=date(2007, 8, 24),
        latitude=58.4394,
        longitude=1.8875,
        total_depth_m=3200.0,
    )
    assert wh.well_id == "15/9-F-11B"
    assert wh.latitude == 58.4394
    assert wh.total_depth_m == 3200.0


def test_well_header_latitude_validation():
    with pytest.raises(ValidationError):
        WellHeader(well_id="TEST-1", latitude=95.0)

    with pytest.raises(ValidationError):
        WellHeader(well_id="TEST-1", latitude=-95.0)


def test_well_header_longitude_validation():
    with pytest.raises(ValidationError):
        WellHeader(well_id="TEST-1", longitude=185.0)

    with pytest.raises(ValidationError):
        WellHeader(well_id="TEST-1", longitude=-185.0)


def test_drilling_event_valid():
    event = DrillingEvent(
        well_id="15/9-F-11B",
        event_type=EventType.MUD_LOSS,
        depth_m=2450.0,
        formation="Hugin",
        description="Lost 15 bbl/hr mud",
        symptom="Pit volume decreased",
        action_taken="Pumped LCM pill",
        confidence=Confidence.HIGH,
        source_page=3,
        source_snippet="encountered mud loss 15 bbl/hr",
    )
    assert event.event_type == EventType.MUD_LOSS
    assert event.confidence == Confidence.HIGH
    assert event.depth_m == 2450.0


def test_drilling_event_invalid_event_type():
    with pytest.raises(ValidationError):
        DrillingEvent(
            well_id="TEST-1",
            event_type="invalid_type",
            description="some description",
        )


def test_extraction_result_model():
    wh = WellHeader(well_id="15/9-F-11B")
    event = DrillingEvent(
        well_id="15/9-F-11B",
        event_type=EventType.STUCK_PIPE,
        description="Stuck pipe during trip",
    )
    result = ExtractionResult(
        source_doc="wcr.pdf",
        extraction_method=ExtractionMethod.DIGITAL_PARSE,
        well_header=wh,
        events=[event],
        overall_confidence=Confidence.HIGH,
    )
    assert len(result.events) == 1
    assert result.well_header.well_id == "15/9-F-11B"
    assert result.overall_confidence == Confidence.HIGH
