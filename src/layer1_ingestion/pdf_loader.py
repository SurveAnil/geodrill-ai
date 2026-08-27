"""
pdf_loader.py
=============
Digital document ingestion: extracts text layers and tables from PDF reports
and assesses digital-native text density to route scanned/image-based documents.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Union
import pdfplumber

from config.constants import MIN_CHARS_PER_PAGE_FOR_DIGITAL
from src.api.schemas.document_schemas import PageContent, IngestResult


class PDFLoader:
    """Loader and pre-processor for digital and scanned PDF drilling documents."""

    def __init__(self, min_chars_per_page: int = MIN_CHARS_PER_PAGE_FOR_DIGITAL):
        self.min_chars_per_page = min_chars_per_page

    def load(self, file_path: Union[str, Path]) -> IngestResult:
        """
        Extracts text and table content from a PDF file. Evaluates text density
        per page to determine whether the document is digital-native or scanned.
        """
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
                total_chars += len(text.strip())
                if not text.strip():
                    warnings.append(f"Page {i}: no extractable text layer found")
                pages.append(PageContent(page_number=i, text=text, tables=tables))

        avg_chars_per_page = total_chars / num_pages if num_pages else 0
        is_digital_native = avg_chars_per_page >= self.min_chars_per_page

        if not is_digital_native:
            warnings.append(
                f"Low average text density ({avg_chars_per_page:.0f} chars/page) — "
                "this document is likely scanned or image-based. Routing to VLM/OCR path."
            )

        full_text = "\n\n".join(
            f"[PAGE {p.page_number}]\n{p.text}" for p in pages
        )

        return IngestResult(
            file_path=path_str,
            is_digital_native=is_digital_native,
            pages=pages,
            full_text=full_text,
            warnings=warnings,
        )


def ingest_pdf(file_path: Union[str, Path], min_chars_per_page: int = MIN_CHARS_PER_PAGE_FOR_DIGITAL) -> IngestResult:
    """Convenience functional wrapper around PDFLoader."""
    loader = PDFLoader(min_chars_per_page=min_chars_per_page)
    return loader.load(file_path)
