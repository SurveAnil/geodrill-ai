"""
document_pipeline.py
====================
End-to-end ingestion and extraction pipeline orchestrator.
Executes multi-pass structured extraction:
  Pass 1: Well Header & Drilling Incidents / Events -> DB & Vector Store
  Pass 2: Geological Formation Tops, Casing Programs, Cementing Records, & Mud Programs -> DB Store
Fault-isolated: failure in Pass 2 does not discard or roll back Pass 1 extractions.
"""

from __future__ import annotations

import glob
import logging
import os
from pathlib import Path
from typing import List, Optional, Union

from src.api.schemas.document_schemas import (
    ExtractionMethod,
    ExtractionResult,
    DocumentProcessResponse,
)
from src.api.schemas.incident_schemas import WellHeader, Confidence
from src.layer1_ingestion.pdf_loader import PDFLoader
from src.layer1_ingestion.ocr_engine import OCREngine
from src.layer4_knowledge_graph.db_service import DatabaseService, db_service
from src.layer4_knowledge_graph.vector_store import VectorStore, vector_store
from src.layer5_copilot.llm_extractor import (
    LLMClient,
    run_extraction,
    run_program_extraction,
    get_llm_client,
)

logger = logging.getLogger(__name__)


class DocumentPipeline:
    """Orchestrates document reading, routing, structured multi-pass extraction, persistence, and vector indexing."""

    def __init__(
        self,
        pdf_loader: Optional[PDFLoader] = None,
        ocr_engine: Optional[OCREngine] = None,
        db: Optional[DatabaseService] = None,
        v_store: Optional[VectorStore] = None,
        llm_client: Optional[LLMClient] = None,
    ):
        self.pdf_loader = pdf_loader or PDFLoader()
        self.ocr_engine = ocr_engine or OCREngine()
        self.db = db or db_service
        self.vector_store = v_store or vector_store
        self.llm_client = llm_client or get_llm_client()

    def process_document(
        self,
        file_path: Union[str, Path],
        persist: bool = True,
        llm_client: Optional[LLMClient] = None,
        source_doc_name: Optional[str] = None,
    ) -> ExtractionResult:
        """
        Executes complete multi-pass extraction workflow on a single document:
        1. Ingest PDF and analyze text density.
        2. Route scanned vs digital documents.
        3. Pass 1: Extract structured well header and drilling events via LLM.
        4. Validate against Pydantic domain models.
        5. Persist well, incident, and document status records to database.
        6. Embed and index all extracted events into Chroma vector store inline.
        7. Pass 2: Extract well program data (formation tops, casing, cementing, mud program).
        8. Persist well program data in isolated transaction (failures do not roll back Pass 1).
        """
        path_str = str(file_path)
        doc_identifier = source_doc_name or os.path.basename(path_str)
        logger.info("Processing document: %s (identifier: %s)", path_str, doc_identifier)

        # Step 1: Ingestion & Text extraction
        ingest_result = self.pdf_loader.load(path_str)

        # Step 2: Routing
        if not ingest_result.is_digital_native:
            logger.warning(
                "Document %s has low text density; flagging for manual/OCR review.",
                path_str,
            )
            result = ExtractionResult(
                source_doc=doc_identifier,
                extraction_method=ExtractionMethod.MANUAL_FLAG,
                well_header=WellHeader(well_id="UNKNOWN"),
                events=[],
                formation_tops=[],
                casing_program=[],
                cementing_records=[],
                mud_program=[],
                overall_confidence=Confidence.LOW,
                processing_notes="Low text density; routed as scanned document needing OCR/VLM.",
            )
            if persist:
                self.db.store_extraction_result(result)
            return result

        extraction_method = ExtractionMethod.DIGITAL_PARSE
        client = llm_client or self.llm_client

        # Step 3: Pass 1 — LLM Structured Header & Incident Extraction
        result = run_extraction(
            document_text=ingest_result.full_text,
            source_doc=doc_identifier,
            extraction_method=extraction_method,
            client=client,
        )
        result.source_doc = doc_identifier

        # Step 4: Storage & Inline Vector Embedding for Pass 1
        if persist:
            persisted_events = self.db.store_extraction_result(result)
            for event_id, event in persisted_events:
                try:
                    self.vector_store.embed_and_upsert(
                        event=event,
                        event_id=event_id,
                        source_doc=result.source_doc,
                        source_page=event.source_page,
                        source_snippet=event.source_snippet,
                    )
                except Exception as exc:
                    logger.error("Failed to embed event %d into vector store: %s", event_id, exc)

            logger.info(
                "Successfully stored and indexed Pass 1 extraction for well %s (%d events) from %s",
                result.well_header.well_id,
                len(result.events),
                doc_identifier,
            )

        # Step 5: Pass 2 — LLM Well Program Data Extraction (Formation Tops, Casing, Cementing, Mud)
        try:
            program_data = run_program_extraction(
                document_text=ingest_result.full_text,
                source_doc=doc_identifier,
                extraction_method=extraction_method,
                client=client,
            )
            result.formation_tops = program_data.formation_tops
            result.casing_program = program_data.casing_program
            result.cementing_records = program_data.cementing_records
            result.mud_program = program_data.mud_program

            if persist and (
                program_data.formation_tops
                or program_data.casing_program
                or program_data.cementing_records
                or program_data.mud_program
            ):
                self.db.store_program_data(
                    source_doc=doc_identifier,
                    formation_tops=program_data.formation_tops,
                    casing_program=program_data.casing_program,
                    cementing_records=program_data.cementing_records,
                    mud_program=program_data.mud_program,
                )
                logger.info(
                    "Successfully stored Pass 2 program data for %s: %d formation tops, %d casing strings, %d cementing records, %d mud intervals",
                    doc_identifier,
                    len(program_data.formation_tops),
                    len(program_data.casing_program),
                    len(program_data.cementing_records),
                    len(program_data.mud_program),
                )
        except Exception as exc:
            logger.warning(
                "Pass 2 program data extraction encountered an error for %s: %s (Pass 1 data remains intact)",
                doc_identifier,
                exc,
            )
            if result.processing_notes:
                result.processing_notes += f"; Program data extraction warning: {exc}"
            else:
                result.processing_notes = f"Program data extraction warning: {exc}"

        return result

    def process_directory(
        self,
        directory_path: Union[str, Path],
        pattern: str = "*.pdf",
        persist: bool = True,
    ) -> List[ExtractionResult]:
        """Processes all matching PDF documents in a directory."""
        dir_str = str(directory_path)
        search_pattern = os.path.join(dir_str, pattern)
        file_paths = sorted(glob.glob(search_pattern))
        logger.info("Found %d PDF file(s) in %s", len(file_paths), dir_str)

        results: List[ExtractionResult] = []
        for file_path in file_paths:
            try:
                res = self.process_document(file_path, persist=persist)
                results.append(res)
            except Exception as exc:
                logger.error("Failed to process document %s: %s", file_path, exc)
                doc_name = os.path.basename(file_path)
                failed_res = ExtractionResult(
                    source_doc=doc_name,
                    extraction_method=ExtractionMethod.MANUAL_FLAG,
                    well_header=WellHeader(well_id="UNKNOWN"),
                    events=[],
                    formation_tops=[],
                    casing_program=[],
                    cementing_records=[],
                    mud_program=[],
                    overall_confidence=Confidence.LOW,
                    processing_notes=f"Pipeline execution error: {exc}",
                )
                if persist:
                    self.db.store_extraction_result(failed_res)
                results.append(failed_res)

        return results


# Default singleton instance
pipeline = DocumentPipeline()
