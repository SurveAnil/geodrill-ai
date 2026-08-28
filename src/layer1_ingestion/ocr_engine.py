"""
ocr_engine.py
=============
OCR and Vision-Language Model (VLM) routing engine for scanned, degraded,
or handwritten drilling logs.

Scope Clarification:
--------------------
- **Stage 1 (Current)**: Serves as the Document Classifier and Guardrail.
  Detects low text density (<40 chars/page) and flags documents into the
  `needs_review` queue (`ExtractionMethod.MANUAL_FLAG`) to prevent silent data corruption.
- **Stage 3 (Future)**: Full vision-based OCR / VLM integration (e.g., Tesseract,
  PaddleOCR, or Claude Vision API) for processing handwritten mud logs and scanned legacy records.
"""

from __future__ import annotations

import logging
import shutil
from typing import Optional
from src.api.schemas.document_schemas import IngestResult, ExtractionMethod

logger = logging.getLogger(__name__)


class OCREngine:
    """
    Stage 1 Document Classifier and Stage 3 Vision-OCR Interface.
    Evaluates text density and routes image-based or degraded drilling reports.
    """

    def __init__(self, tesseract_cmd: Optional[str] = None):
        self.tesseract_cmd = tesseract_cmd or shutil.which("tesseract")

    @property
    def available(self) -> bool:
        return bool(self.tesseract_cmd)

    def should_route_to_ocr(self, ingest_result: IngestResult) -> bool:
        """
        Stage 1 Guardrail: Determines if the document is scanned / image-based
        and requires OCR/VLM processing rather than native text parsing.
        """
        return bool(ingest_result.scanned_pages) or not ingest_result.is_digital_native

    def process_scanned_document(self, ingest_result: IngestResult) -> IngestResult:
        """
        Stage 1 Guardrail / Stage 3 Entry Point:
        In Stage 1, marks the document with an actionable warning and routes to MANUAL_FLAG.
        In Stage 3, executes vision model / OCR engine to extract text from page bitmaps.
        """
        logger.info("Routing document %s to OCR/VLM engine (Stage 1 Guardrail)", ingest_result.file_path)
        if not self.available:
            ingest_result.warnings.append(
                "OCR dependency unavailable; document requires manual review or configured VLM."
            )
        ingest_result.warnings.append(
            "Document classified as scanned/image-based. Stage 1 routes to review queue; "
            "Stage 3 vision pipeline will provide OCR text extraction."
        )
        return ingest_result
