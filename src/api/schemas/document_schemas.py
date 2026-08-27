"""
document_schemas.py
===================
Data contract defining ingestion payloads, PDF page contents, extraction methods,
and complete document extraction results.
"""

from __future__ import annotations

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field

from src.api.schemas.incident_schemas import WellHeader, DrillingEvent, Confidence
from src.api.schemas.well_program_schemas import (
    FormationTop,
    CasingProgram,
    CementingRecord,
    MudProgramEntry,
)


class ExtractionMethod(str, Enum):
    DIGITAL_PARSE = "digital_parse"   # Text layer extracted directly from native PDF
    VLM_OCR = "vlm_ocr"               # Vision / OCR model used for scanned or degraded page
    MANUAL_FLAG = "manual_flag"       # Extraction failed or needs human validation


class PageContent(BaseModel):
    """Extracted text and structured table data per document page."""
    page_number: int
    text: str
    tables: List[List[List[Optional[str]]]] = Field(default_factory=list)


class IngestResult(BaseModel):
    """Result of document loading and digital-native character density detection."""
    file_path: str
    is_digital_native: bool
    pages: List[PageContent] = Field(default_factory=list)
    full_text: str = ""
    warnings: List[str] = Field(default_factory=list)


class ExtractionResult(BaseModel):
    """The complete structured extraction output for one processed document."""
    source_doc: str
    extraction_method: ExtractionMethod
    well_header: WellHeader
    events: List[DrillingEvent] = Field(default_factory=list)
    formation_tops: List[FormationTop] = Field(default_factory=list)
    casing_program: List[CasingProgram] = Field(default_factory=list)
    cementing_records: List[CementingRecord] = Field(default_factory=list)
    mud_program: List[MudProgramEntry] = Field(default_factory=list)
    overall_confidence: Confidence = Confidence.MEDIUM
    processing_notes: Optional[str] = Field(
        None, description="Warnings or contextual notes from the extraction pipeline"
    )


class DocumentProcessResponse(BaseModel):
    """API response model for document ingestion & extraction execution."""
    success: bool
    source_doc: str
    extraction_result: Optional[ExtractionResult] = None
    warnings: List[str] = Field(default_factory=list)
    message: Optional[str] = None


class DocumentReviewItem(BaseModel):
    """Document queue item needing manual engineer review."""
    source_doc: str
    extraction_method: ExtractionMethod
    overall_confidence: Confidence
    processing_notes: Optional[str] = None
    needs_review: bool = True
