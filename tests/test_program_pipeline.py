"""
test_program_pipeline.py
========================
Tests for multi-pass extraction orchestration, well-program persistence,
cross-well casing correlation by formation, and transaction failure isolation.
"""

import os
import pytest

from src.api.schemas.document_schemas import ExtractionMethod
from src.layer1_ingestion.document_pipeline import DocumentPipeline
from src.layer4_knowledge_graph.db_service import DatabaseService
from src.layer5_copilot.llm_extractor import MockLLMClient, LLMClient


class FailingPass2MockClient(MockLLMClient):
    """Mock client that succeeds on Pass 1 but throws an error on Pass 2."""

    def extract_program_data(self, document_text: str, source_doc: str, extraction_method: ExtractionMethod) -> dict:
        raise RuntimeError("Simulated network timeout or schema crash during Pass 2 program data extraction")


@pytest.fixture
def temp_db(tmp_path):
    db_file = str(tmp_path / "test_program_pipe.db")
    service = DatabaseService(db_path=db_file)
    service.init_db()
    return service


@pytest.fixture
def sample_reports_dir():
    base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "sample_reports")
    return base_dir


def test_two_pass_extraction_and_storage(temp_db, sample_reports_dir):
    wcr_pdf = os.path.join(sample_reports_dir, "wcr_volve_15_9_f11b.pdf")
    if not os.path.exists(wcr_pdf):
        pytest.skip(f"Sample PDF {wcr_pdf} not found")

    mock_client = MockLLMClient()
    pipeline = DocumentPipeline(db=temp_db, llm_client=mock_client)

    result = pipeline.process_document(wcr_pdf, persist=True)

    # Verify Pass 1 data
    assert result.well_header.well_id == "15/9-F-11B"
    assert len(result.events) == 2

    # Verify Pass 2 data attached to result
    assert len(result.formation_tops) == 2
    assert len(result.casing_program) == 2
    assert len(result.cementing_records) == 1
    assert len(result.mud_program) == 1

    # Verify Database Tables
    with temp_db.get_connection() as conn:
        tops = conn.execute("SELECT * FROM formation_tops WHERE well_id = '15/9-F-11B'").fetchall()
        assert len(tops) == 2

        casings = conn.execute("SELECT * FROM casing_program WHERE well_id = '15/9-F-11B'").fetchall()
        assert len(casings) == 2

        cement = conn.execute("SELECT * FROM cementing_records WHERE well_id = '15/9-F-11B'").fetchall()
        assert len(cement) == 1

        mud = conn.execute("SELECT * FROM mud_program WHERE well_id = '15/9-F-11B'").fetchall()
        assert len(mud) == 1


def test_cross_well_casing_query_by_formation(temp_db, sample_reports_dir):
    wcr_pdf = os.path.join(sample_reports_dir, "wcr_volve_15_9_f11b.pdf")
    ddr_pdf = os.path.join(sample_reports_dir, "ddr_volve_15_9_f12.pdf")
    if not os.path.exists(wcr_pdf) or not os.path.exists(ddr_pdf):
        pytest.skip("Sample PDFs not found")

    mock_client = MockLLMClient()
    pipeline = DocumentPipeline(db=temp_db, llm_client=mock_client)

    # Process both wells
    pipeline.process_document(wcr_pdf, persist=True)
    pipeline.process_document(ddr_pdf, persist=True)

    # Query casing practices across wells drilled in Hugin Formation
    casing_records = temp_db.query_casing_by_formation("Hugin Formation")
    assert len(casing_records) >= 2

    wells_represented = {r["well_id"] for r in casing_records}
    assert "15/9-F-11B" in wells_represented
    assert "15/9-F-12" in wells_represented

    # Verify casing and cementing fields are present
    first_rec = casing_records[0]
    assert "casing_type" in first_rec
    assert "casing_depth_set_m" in first_rec
    assert "formation_top_depth_m" in first_rec


def test_pass2_failure_does_not_rollback_pass1(temp_db, sample_reports_dir):
    wcr_pdf = os.path.join(sample_reports_dir, "wcr_volve_15_9_f11b.pdf")
    if not os.path.exists(wcr_pdf):
        pytest.skip(f"Sample PDF {wcr_pdf} not found")

    # Use failing Pass 2 client
    failing_client = FailingPass2MockClient()
    pipeline = DocumentPipeline(db=temp_db, llm_client=failing_client)

    result = pipeline.process_document(wcr_pdf, persist=True)

    # Verify Pass 1 data was preserved and committed
    assert result.well_header.well_id == "15/9-F-11B"
    assert len(result.events) == 2

    # Verify DB has well header and events despite Pass 2 failure
    with temp_db.get_connection() as conn:
        well_row = conn.execute("SELECT * FROM wells WHERE well_id = '15/9-F-11B'").fetchone()
        assert well_row is not None

        event_rows = conn.execute("SELECT * FROM events WHERE well_id = '15/9-F-11B'").fetchall()
        assert len(event_rows) == 2

    # Verify warning note is present in result processing_notes
    assert result.processing_notes is not None
    assert "Program data extraction" in result.processing_notes
