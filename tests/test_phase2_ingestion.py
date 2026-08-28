"""Targeted coverage for Phase 2 supported formats and provenance context."""

import zipfile

from src.api.schemas.document_schemas import IngestResult, PageContent
from src.layer1_ingestion.pdf_loader import PDFLoader
from src.layer1_ingestion.table_extractor import format_document_tables_as_text


def test_docx_loader_extracts_text_and_tables(tmp_path):
    path = tmp_path / "report.docx"
    document = """<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
      <w:body><w:p><w:r><w:t>Well 15/9-F-12</w:t></w:r></w:p>
      <w:tbl><w:tr><w:tc><w:p><w:r><w:t>Depth</w:t></w:r></w:p></w:tc>
      <w:tc><w:p><w:r><w:t>2500</w:t></w:r></w:p></w:tc></w:tr></w:tbl>
      </w:body></w:document>"""
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("word/document.xml", document)

    result = PDFLoader().load_supported(path)
    assert result.document_type == "docx"
    assert "15/9-F-12" in result.full_text
    assert "[Table 1 on page 1]" in result.full_text
    assert "2500" in result.full_text


def test_supported_text_formats_are_ingested(tmp_path):
    las = tmp_path / "well.las"
    las.write_text("~Version\nVERS. 2.0\n~Well\nWELL. 15/9-F-1\n", encoding="utf-8")
    witsml = tmp_path / "well.witsml"
    witsml.write_text("<witsml><well uid='1'>15/9-F-1</well></witsml>", encoding="utf-8")

    assert PDFLoader().load_supported(las).document_type == "las"
    assert PDFLoader().load_supported(witsml).document_type == "witsml"


def test_table_context_retains_page_provenance():
    context = format_document_tables_as_text([
        PageContent(page_number=7, text="", tables=[[["Key", "Value"]]])
    ])
    assert "[Table 1 on page 7]" in context
    assert "| Key | Value |" in context


def test_ingest_result_tracks_mixed_pages():
    result = IngestResult(
        file_path="mixed.pdf", is_digital_native=False,
        pages=[
            PageContent(page_number=1, text="native text", is_digital_native=True),
            PageContent(page_number=2, text="", is_digital_native=False),
        ],
        digital_pages=[1], scanned_pages=[2], is_mixed=True,
    )
    assert result.is_mixed
    assert result.digital_pages == [1]
    assert result.scanned_pages == [2]
