"""
test_pipeline.py
================
Unit tests for DocumentPipeline orchestration.
"""

import tempfile
import os
from unittest.mock import MagicMock
import pytest

from src.api.schemas.document_schemas import IngestResult, PageContent, ExtractionMethod
from src.api.schemas.incident_schemas import Confidence
from src.layer1_ingestion.document_pipeline import DocumentPipeline
from src.layer1_ingestion.pdf_loader import PDFLoader
from src.layer4_knowledge_graph.db_service import DatabaseService
from src.layer5_copilot.llm_extractor import MockLLMClient


@pytest.fixture
def temp_pipeline():
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    db = DatabaseService(db_path=path)
    db.init_db()

    mock_loader = MagicMock(spec=PDFLoader)
    pipe = DocumentPipeline(
        pdf_loader=mock_loader,
        db=db,
        llm_client=MockLLMClient(),
    )
    yield pipe, mock_loader, db
    if os.path.exists(path):
        os.remove(path)


def test_pipeline_digital_document_flow(temp_pipeline):
    pipe, mock_loader, db = temp_pipeline

    mock_loader.load.return_value = IngestResult(
        file_path="mock_well_report.pdf",
        is_digital_native=True,
        pages=[
            PageContent(
                page_number=1,
                text="Well Completion Report for WELL-15/9-F-11B in Volve field.",
            )
        ],
        full_text="Well Completion Report for WELL-15/9-F-11B in Volve field.",
    )

    result = pipe.process_document("mock_well_report.pdf", persist=True)

    assert result.well_header.well_id == "15/9-F-11B"
    assert result.extraction_method == ExtractionMethod.DIGITAL_PARSE
    assert len(result.events) == 2
    assert result.overall_confidence == Confidence.HIGH

    # Verify DB persistence
    stored_well = db.get_well("15/9-F-11B")
    assert stored_well is not None
    assert stored_well["operator"] == "Statoil ASA"


def test_pipeline_scanned_document_routing(temp_pipeline):
    pipe, mock_loader, db = temp_pipeline

    mock_loader.load.return_value = IngestResult(
        file_path="scanned_handwritten.pdf",
        is_digital_native=False,
        pages=[],
        full_text="",
        warnings=["Low average text density"],
    )

    result = pipe.process_document("scanned_handwritten.pdf", persist=True)

    assert result.extraction_method == ExtractionMethod.MANUAL_FLAG
    assert result.overall_confidence == Confidence.LOW
    assert result.well_header.well_id == "UNKNOWN"

    review_queue = db.get_documents_needing_review()
    assert len(review_queue) == 1
    assert review_queue[0].source_doc == "scanned_handwritten.pdf"
