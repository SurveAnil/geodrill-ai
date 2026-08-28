"""
test_llm_extractor.py
=====================
Unit tests for LLM extraction, provider fallbacks, and schema validation.
"""

from src.api.schemas.document_schemas import ExtractionMethod
from src.api.schemas.incident_schemas import Confidence, EventType
from src.layer5_copilot.llm_extractor import (
    MockLLMClient,
    FallbackLLMClient,
    run_extraction,
)


def test_mock_llm_client_known_document():
    client = MockLLMClient()
    raw = client.extract(
        document_text="Report for WELL-15/9-F-11B in Volve Field",
        source_doc="wcr_15_9_f11b.pdf",
        extraction_method=ExtractionMethod.DIGITAL_PARSE,
    )
    assert raw["well_header"]["well_id"] == "15/9-F-11B"
    assert len(raw["events"]) == 2
    assert raw["overall_confidence"] == "high"


def test_mock_llm_client_unknown_document():
    client = MockLLMClient()
    raw = client.extract(
        document_text="Unrelated text about something else",
        source_doc="other.pdf",
        extraction_method=ExtractionMethod.DIGITAL_PARSE,
    )
    assert raw["well_header"]["well_id"] == "UNKNOWN"
    assert raw["overall_confidence"] == "low"
    assert len(raw["events"]) == 0


def test_mock_llm_client_demo_nwis_document_extracts_events():
    raw = MockLLMClient().extract(
        "Report ID DEMO-NWIS-WCR-001 for well NWIS-DEMO-01.",
        "demo_nwis_multi_event_report.pdf",
        ExtractionMethod.DIGITAL_PARSE,
    )
    assert raw["well_header"]["well_id"] == "NWIS-DEMO-01"
    assert len(raw["events"]) == 6
    assert raw["events"][0]["source_page"] == 1


def test_fallback_llm_client_cascades_to_mock():
    class FailingClient:
        def extract(self, *args, **kwargs):
            raise ConnectionError("Provider API timeout")

    fallback = FallbackLLMClient(providers=[FailingClient()])
    raw = fallback.extract(
        document_text="Report for 15/9-F-11B",
        source_doc="doc.pdf",
        extraction_method=ExtractionMethod.DIGITAL_PARSE,
    )
    assert raw["well_header"]["well_id"] == "15/9-F-11B"


def test_run_extraction_success():
    client = MockLLMClient()
    result = run_extraction(
        document_text="WELL-15/9-F-11B summary",
        source_doc="wcr.pdf",
        extraction_method=ExtractionMethod.DIGITAL_PARSE,
        client=client,
    )
    assert result.well_header.well_id == "15/9-F-11B"
    assert len(result.events) == 2
    assert result.events[0].event_type == EventType.MUD_LOSS
    assert result.overall_confidence == Confidence.HIGH


def test_run_extraction_schema_error_recovery():
    class BadSchemaClient:
        def extract(self, *args, **kwargs):
            # Missing required well_id
            return {"well_header": {}, "events": []}

    result = run_extraction(
        document_text="text",
        source_doc="doc.pdf",
        extraction_method=ExtractionMethod.DIGITAL_PARSE,
        client=BadSchemaClient(),
    )
    assert result.extraction_method == ExtractionMethod.MANUAL_FLAG
    assert result.overall_confidence == Confidence.LOW
    assert "Schema validation failed" in (result.processing_notes or "")
