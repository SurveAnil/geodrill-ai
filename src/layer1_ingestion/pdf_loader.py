"""
pdf_loader.py
=============
Digital document ingestion: extracts text layers and tables from PDF reports
and assesses digital-native text density to route scanned/image-based documents.
"""

from __future__ import annotations

import os
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Union
import pdfplumber

from config.constants import MIN_CHARS_PER_PAGE_FOR_DIGITAL
from src.api.schemas.document_schemas import PageContent, IngestResult
from src.layer1_ingestion.table_extractor import format_document_tables_as_text


class PDFLoader:
    """Loader and pre-processor for digital and scanned PDF drilling documents."""

    def __init__(self, min_chars_per_page: int = MIN_CHARS_PER_PAGE_FOR_DIGITAL):
        self.min_chars_per_page = min_chars_per_page

    def load(self, file_path: Union[str, Path]) -> IngestResult:
        """
        Extracts text and table content from a PDF file. Evaluates text density
        per page to determine whether the document is digital-native or scanned.
        """
        if Path(file_path).suffix.lower() != ".pdf":
            return self.load_supported(file_path)
        path_str = str(file_path)
        if not os.path.exists(path_str):
            raise FileNotFoundError(f"PDF document not found: {path_str}")

        pages: list[PageContent] = []
        warnings: list[str] = []
        total_chars = 0

        with pdfplumber.open(path_str) as pdf:
            num_pages = len(pdf.pages)
            for i, page in enumerate(pdf.pages, start=1):
                text = page.extract_text() or ""
                tables = page.extract_tables() or []
                table_chars = sum(
                    len(str(cell or ""))
                    for table in tables for row in table for cell in row
                )
                page_chars = len(text.strip()) + table_chars
                total_chars += page_chars
                if page_chars < self.min_chars_per_page:
                    warnings.append(f"Page {i}: no extractable text layer found")
                pages.append(PageContent(
                    page_number=i, text=text, tables=tables,
                    is_digital_native=page_chars >= self.min_chars_per_page,
                ))

        avg_chars_per_page = total_chars / num_pages if num_pages else 0
        digital_pages = [p.page_number for p in pages if p.is_digital_native]
        scanned_pages = [p.page_number for p in pages if not p.is_digital_native]
        is_digital_native = bool(pages) and not scanned_pages

        if scanned_pages:
            warnings.append(
                f"Pages {scanned_pages} have low text density; routing those pages to VLM/OCR review."
            )
        if digital_pages and scanned_pages:
            warnings.append("Mixed PDF: digital pages remain available for extraction; scanned pages need OCR/review.")

        full_text = "\n\n".join(
            f"[PAGE {p.page_number}]\n{p.text}" for p in pages
        )
        table_text = format_document_tables_as_text(pages)
        if table_text:
            full_text += "\n\n--- EXTRACTED TABLES (with provenance) ---\n" + table_text

        return IngestResult(
            file_path=path_str,
            is_digital_native=is_digital_native,
            pages=pages,
            full_text=full_text,
            warnings=warnings,
            document_type="pdf",
            scanned_pages=scanned_pages,
            digital_pages=digital_pages,
            is_mixed=bool(digital_pages and scanned_pages),
        )

    def load_supported(self, file_path: Union[str, Path]) -> IngestResult:
        """Load PDF, DOCX, LAS, or WITSML using dependencies already in the project."""
        suffix = Path(file_path).suffix.lower()
        if suffix == ".pdf":
            return self.load(file_path)
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Document not found: {file_path}")
        if suffix == ".docx":
            with zipfile.ZipFile(file_path) as archive:
                root = ET.fromstring(archive.read("word/document.xml"))
            ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
            paragraphs = ["".join(node.text or "" for node in p.findall(".//w:t", ns))
                          for p in root.findall(".//w:p", ns)]
            tables = []
            for table in root.findall(".//w:tbl", ns):
                rows = []
                for row in table.findall("./w:tr", ns):
                    rows.append(["".join(node.text or "" for node in cell.findall(".//w:t", ns))
                                 for cell in row.findall("./w:tc", ns)])
                if rows:
                    tables.append(rows)
            page = PageContent(page_number=1, text="\n".join(p for p in paragraphs if p),
                               tables=tables, is_digital_native=True)
            full_text = page.text
            table_text = format_document_tables_as_text([page])
            if table_text:
                full_text += "\n\n--- EXTRACTED TABLES (with provenance) ---\n" + table_text
            return IngestResult(file_path=str(file_path), is_digital_native=True,
                                pages=[page], full_text=full_text,
                                document_type="docx", digital_pages=[1])
        raw = Path(file_path).read_text(encoding="utf-8-sig", errors="replace")
        if suffix == ".las":
            text = raw
            document_type = "las"
        elif suffix == ".witsml":
            text = raw
            document_type = "witsml"
        else:
            raise ValueError(f"Unsupported document format: {suffix}")
        page = PageContent(page_number=1, text=text, is_digital_native=bool(text.strip()))
        return IngestResult(file_path=str(file_path), is_digital_native=bool(text.strip()),
                            pages=[page], full_text="[PAGE 1]\n" + text,
                            document_type=document_type, digital_pages=[1] if text.strip() else [],
                            scanned_pages=[] if text.strip() else [1])


def ingest_pdf(file_path: Union[str, Path], min_chars_per_page: int = MIN_CHARS_PER_PAGE_FOR_DIGITAL) -> IngestResult:
    """Convenience functional wrapper around PDFLoader."""
    loader = PDFLoader(min_chars_per_page=min_chars_per_page)
    return loader.load(file_path)


def ingest_supported_document(file_path: Union[str, Path]) -> IngestResult:
    """Convenience wrapper for all formats accepted by the upload API."""
    return PDFLoader().load_supported(file_path)
