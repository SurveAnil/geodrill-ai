"""
test_ingestion.py
=================
Unit tests for PDF table extraction and density detection.
"""

from src.api.schemas.document_schemas import PageContent, IngestResult
from src.layer1_ingestion.table_extractor import format_tables_as_text, extract_key_value_pairs
from src.layer1_ingestion.ocr_engine import OCREngine


def test_format_tables_as_text():
    page = PageContent(
        page_number=1,
        text="Sample text",
        tables=[
            [["Well Name", "15/9-F-11B"], ["Operator", "Statoil"]],
        ],
    )
    formatted = format_tables_as_text(page)
    assert "[Table 1 on page 1]" in formatted
    assert "| Well Name | Statoil |" in formatted or "15/9-F-11B" in formatted


def test_extract_key_value_pairs():
    tables = [
        [["Field", "Volve"], ["Country", "Norway"]],
    ]
    kvs = extract_key_value_pairs(tables)
    assert kvs.get("Field") == "Volve"
    assert kvs.get("Country") == "Norway"


def test_ocr_engine_routing():
    engine = OCREngine()
    digital_result = IngestResult(
        file_path="digital.pdf",
        is_digital_native=True,
        full_text="Long page text with plenty of content...",
    )
    scanned_result = IngestResult(
        file_path="scanned.pdf",
        is_digital_native=False,
        full_text="",
    )
    assert not engine.should_route_to_ocr(digital_result)
    assert engine.should_route_to_ocr(scanned_result)
